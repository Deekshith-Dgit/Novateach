from typing import Any, Optional

from services.quiz_session_service import (
    start_quiz_session,
    get_quiz_session,
    complete_quiz_session,
    get_retest_targets_for_session_concept,
    save_session_questions,
    get_session_question_ids,
    is_session_question_answered,
    mark_session_question_answered,
)

from services.question_service import (
    get_questions_for_graph,
    get_question,
)

from services.learner_state_service import (
    record_quiz_result,
    complete_retest_target,
)

from services.error_diagnosis_service import (
    diagnose_error,
)


def create_quiz_for_graph(
    username: str,
    graph_id: int,
    topic: str,
    question_count: int = 5,
    purpose: str = "diagnostic",
    difficulty: str = "standard",
    cognitive_skill: Optional[str] = None,
) -> dict[str, Any]:
    """
    Creates a quiz session using already saved questions
    from a specific knowledge graph.

    The exact selected question IDs are saved so that
    the same quiz can be loaded later.
    """

    if question_count < 1:
        raise ValueError("question_count must be at least 1")

    questions = get_questions_for_graph(
        graph_id=graph_id,
        difficulty=difficulty,
        cognitive_skill=cognitive_skill,
        limit=question_count,
    )

    if not questions:
        raise ValueError(
            "No validated questions found for this graph. "
            "Generate questions first."
        )

    session_id = start_quiz_session(
        username=username,
        topic=topic,
        purpose=purpose,
        difficulty=difficulty,
        question_count=len(questions),
        graph_id=graph_id,
    )

    # Save the exact questions selected for this session.
    save_session_questions(
        session_id=session_id,
        question_ids=[
            question["id"]
            for question in questions
        ],
    )

    return {
        "session_id": session_id,
        "username": username,
        "topic": topic,
        "graph_id": graph_id,
        "purpose": purpose,
        "difficulty": difficulty,
        "questions": questions,
        "current_index": 0,
        "completed": False,
    }


def load_quiz(
    session_id: int,
) -> dict[str, Any]:
    """
    Loads a quiz session and the exact questions
    originally assigned to that session.

    Older sessions created before exact question
    persistence are supported through a fallback.
    """

    session = get_quiz_session(session_id)

    if session is None:
        raise ValueError(
            f"No quiz session found with ID: {session_id}"
        )

    question_ids = get_session_question_ids(session_id)

    if question_ids:
        questions = []

        for question_id in question_ids:
            question = get_question(question_id)

            if question is not None:
                questions.append(question)

    else:
        # Backward compatibility for old sessions.
        if session["graph_id"] is None:
            raise ValueError(
                "This quiz session has no graph_id attached."
            )

        questions = get_questions_for_graph(
            graph_id=session["graph_id"],
            difficulty=session["difficulty"],
            limit=session["question_count"],
        )

    return {
        "session": session,
        "questions": questions,
        "current_index": 0,
        "completed": bool(session["completed"]),
    }


def normalize_answer(
    answer: Any,
) -> str:
    """
    Normalizes answers for simple text comparison.
    """

    if answer is None:
        return ""

    return " ".join(
        str(answer)
        .strip()
        .lower()
        .split()
    )


def evaluate_simple_answer(
    student_answer: Any,
    expected_answer: Any,
) -> str:
    """
    Basic evaluator for exact/normalized answer matching.

    Returns:
        correct
        incorrect
        skipped
    """

    student = normalize_answer(student_answer)
    expected = normalize_answer(expected_answer)

    if not student:
        return "skipped"

    if student == expected:
        return "correct"

    return "incorrect"


def submit_quiz_answer(
    username: str,
    session_id: int,
    question_id: int,
    student_answer: Any,
    error_category: Optional[str] = None,
    error_pattern_key: Optional[str] = None,
    error_description: Optional[str] = None,
    used_hint: bool = False,
    response_time_seconds: Optional[float] = None,
    evaluator_notes: Optional[str] = None,
) -> dict[str, Any]:
    """
    Evaluates and records one quiz answer.

    Flow:

        Student answer
              ↓
        Session validation
              ↓
        Question validation
              ↓
        Duplicate-answer protection
              ↓
        Basic evaluation
              ↓
        Error diagnosis if needed
              ↓
        Learner state update
              ↓
        Retest target resolution if applicable
    """

    # ---------------------------------------------------------
    # 1. Validate quiz session
    # ---------------------------------------------------------

    session = get_quiz_session(session_id)

    if session is None:
        raise ValueError(
            f"No quiz session found with ID: {session_id}"
        )

    if session["username"] != username:
        raise ValueError(
            "This quiz session does not belong to this user."
        )

    if session["completed"]:
        raise ValueError(
            "This quiz session is already completed."
        )

    # ---------------------------------------------------------
    # 2. Load question
    # ---------------------------------------------------------

    question = get_question(question_id)

    if question is None:
        raise ValueError(
            f"No question found with ID: {question_id}"
        )

    # If exact question persistence exists for this session,
    # make sure the submitted question is actually part of it.
    session_question_ids = get_session_question_ids(
        session_id
    )

    if session_question_ids:

        if question_id not in session_question_ids:
            raise ValueError(
                "Question is not part of this quiz session."
            )

        # -----------------------------------------------------
        # 3. Prevent duplicate submission
        # -----------------------------------------------------

        if is_session_question_answered(
            session_id=session_id,
            question_id=question_id,
        ):
            raise ValueError(
                "Question has already been answered "
                "in this quiz session."
            )

    elif question["graph_id"] != session["graph_id"]:
        # Backward compatibility for old sessions.
        raise ValueError(
            "Question does not belong to this quiz graph."
        )

    # ---------------------------------------------------------
    # 4. Evaluate answer
    # ---------------------------------------------------------

    result = evaluate_simple_answer(
        student_answer=student_answer,
        expected_answer=question["expected_answer"],
    )

    # ---------------------------------------------------------
    # 5. Claim the question as answered
    # ---------------------------------------------------------
    #
    # This happens before learner-state recording so that
    # two simultaneous requests cannot both record evidence.
    #
    # If the question was already claimed by another request,
    # mark_session_question_answered() returns False.
    #

    if session_question_ids:

        claimed = mark_session_question_answered(
            session_id=session_id,
            question_id=question_id,
        )

        if not claimed:
            raise ValueError(
                "Question has already been answered "
                "in this quiz session."
            )

    # ---------------------------------------------------------
    # 6. Diagnose incorrect answer
    # ---------------------------------------------------------

    diagnosis = {
        "category": None,
        "pattern_key": None,
        "description": None,
        "confidence": 0.0,
        "method": None,
    }

    if result == "incorrect":

        diagnosis = diagnose_error(
            student_answer=student_answer,
            expected_answer=question["expected_answer"],
            question=question,
        )

        # Only use automatically diagnosed values when
        # the caller did not explicitly provide them.

        if error_category is None:
            error_category = diagnosis["category"]

        if error_pattern_key is None:
            error_pattern_key = diagnosis["pattern_key"]

        if error_description is None:
            error_description = diagnosis["description"]

    # ---------------------------------------------------------
    # 7. Preserve diagnosis information in evaluator notes
    # ---------------------------------------------------------

    diagnosis_note = None

    if diagnosis["method"] is not None:
        diagnosis_note = (
            f"diagnosis_method={diagnosis['method']}; "
            f"diagnosis_confidence="
            f"{diagnosis['confidence']:.2f}"
        )

    if evaluator_notes and diagnosis_note:

        evaluator_notes = (
            f"{evaluator_notes} | {diagnosis_note}"
        )

    elif diagnosis_note:

        evaluator_notes = diagnosis_note

    # ---------------------------------------------------------
    # 8. Update learner model
    # ---------------------------------------------------------

    learner_state = record_quiz_result(
        username=username,
        session_id=session_id,
        question_id=question_id,
        concept_id=question["concept_id"],
        result=result,
        student_answer=str(student_answer),
        correct_answer=question["expected_answer"],
        question_type=question["question_type"],
        cognitive_skill=question["cognitive_skill"],
        difficulty=question["difficulty"],
        error_category=error_category,
        error_pattern_key=error_pattern_key,
        error_description=error_description,
        diagnosis_confidence=diagnosis["confidence"],
        used_hint=used_hint,
        response_time_seconds=response_time_seconds,
        evaluator_notes=evaluator_notes,
    )

    # ---------------------------------------------------------
    # 9. Get updated concept mastery
    # ---------------------------------------------------------

    concept_state = learner_state.concept_states[
        question["concept_id"]
    ]

    # ---------------------------------------------------------
    # 10. Automatic retest target resolution
    # ---------------------------------------------------------

    retest_resolution = {
        "attempted": False,
        "resolved": False,
        "target_ids": [],
        "resolved_target_ids": [],
        "reason": None,
    }

    if session["purpose"] == "retest":

        retest_resolution["attempted"] = True

        linked_targets = get_retest_targets_for_session_concept(
            session_id=session_id,
            concept_id=question["concept_id"],
        )

        if not linked_targets:

            retest_resolution["reason"] = (
                "No retest target is linked to this "
                "session and concept."
            )

        elif result == "correct":

            retest_resolution["target_ids"] = [
                target["id"]
                for target in linked_targets
            ]

            for target in linked_targets:

                if target["status"] != "active":
                    continue

                resolved = complete_retest_target(
                    username=username,
                    target_id=target["id"],
                )

                if resolved:
                    retest_resolution[
                        "resolved_target_ids"
                    ].append(target["id"])

            retest_resolution["resolved"] = bool(
                retest_resolution[
                    "resolved_target_ids"
                ]
            )

            if retest_resolution["resolved"]:

                retest_resolution["reason"] = (
                    "Correct retest answer resolved the "
                    "linked active retest target."
                )

            else:

                retest_resolution["reason"] = (
                    "No active linked retest target "
                    "needed resolution."
                )

        else:

            retest_resolution["target_ids"] = [
                target["id"]
                for target in linked_targets
            ]

            retest_resolution["reason"] = (
                "Retest answer was not correct. "
                "The linked retest target remains active."
            )

    # ---------------------------------------------------------
    # 11. Return complete result
    # ---------------------------------------------------------

    return {
        "session_id": session_id,
        "question_id": question_id,
        "result": result,
        "correct_answer": question["expected_answer"],
        "explanation": question["explanation"],
        "mastery": concept_state.mastery,
        "concept_status": concept_state.status,
        "concept_trend": concept_state.trend,
        "diagnosis": {
            "category": error_category,
            "pattern_key": error_pattern_key,
            "description": error_description,
            "confidence": diagnosis["confidence"],
            "method": diagnosis["method"],
        },
        "retest_resolution": retest_resolution,
    }


def finish_quiz(
    session_id: int,
) -> bool:
    """
    Marks the quiz session as completed.
    """

    return complete_quiz_session(session_id)