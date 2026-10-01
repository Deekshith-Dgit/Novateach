from typing import Any, Optional

from services.adaptation_service import (
    choose_next_action,
    get_learner_snapshot,
)

from services.learner_state_service import (
    get_retest_targets,
)

from services.question_generation_service import (
    generate_questions_for_concept,
)

from services.quiz_session_service import (
    start_quiz_session,
    link_retest_target_to_session,
)


def get_priority_concept_ids(
    username: str,
    limit: int = 3,
) -> list[int]:
    if limit < 1:
        raise ValueError("limit must be at least 1")

    retest_targets = get_retest_targets(
        username=username,
        limit=limit,
    )

    if retest_targets:
        concept_ids = []

        for target in retest_targets:
            concept_id = target["concept_id"]

            if concept_id not in concept_ids:
                concept_ids.append(concept_id)

        return concept_ids[:limit]

    snapshot = get_learner_snapshot(username)

    priority_concepts = snapshot["weak_concepts"][:limit]

    return [
        concept["concept_id"]
        for concept in priority_concepts
    ]


def create_targeted_retest(
    username: str,
    topic: str,
    subject: str,
    academic_level: str,
    difficulty: str = "standard",
    questions_per_concept: int = 2,
    learner_summary: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Creates a targeted retest from the learner's active weaknesses.

    Important adaptation rule:
    If the adaptation engine identifies a prerequisite repair,
    the retest focuses on the blocking prerequisite first.

    Example:

        Electric Field
             ↑
        Electric Charge

    If Electric Charge is insufficiently mastered:

        Retest → Electric Charge

    Electric Field remains an active weakness/target and can be
    retested after its prerequisite is sufficiently mastered.

    For normal targeted practice/retesting, multiple active targets
    can still be included.
    """

    if questions_per_concept < 1:
        raise ValueError(
            "questions_per_concept must be at least 1"
        )

    decision = choose_next_action(username)
    snapshot = decision["snapshot"]

    retest_targets = get_retest_targets(
        username=username,
        limit=3,
    )

    priority_concepts: list[dict[str, Any]] = []

    # ---------------------------------------------------------
    # PREREQUISITE REPAIR
    # ---------------------------------------------------------
    # The adaptation engine has already determined the immediate
    # learning priority. We should respect that decision instead
    # of blindly testing every active target.
    if decision.get("action") == "prerequisite_repair":
        blocking_prerequisite = decision.get(
            "blocking_prerequisite"
        )

        if blocking_prerequisite is not None:
            blocking_concept_id = blocking_prerequisite.get(
                "concept_id"
            )

            matched_target = None

            for target in retest_targets:
                if (
                    target.get("concept_id")
                    == blocking_concept_id
                ):
                    matched_target = target
                    break

            priority_concepts.append(
                {
                    "concept_id": blocking_concept_id,
                    "graph_id": blocking_prerequisite.get(
                        "graph_id"
                    ),
                    "retest_target_id": (
                        matched_target.get("id")
                        if matched_target
                        else None
                    ),
                    "error_pattern_id": (
                        matched_target.get(
                            "error_pattern_id"
                        )
                        if matched_target
                        else None
                    ),
                    "reason": (
                        matched_target.get("reason")
                        if matched_target
                        else (
                            "Blocking prerequisite requires "
                            "repair before the dependent "
                            "concept is retested."
                        )
                    ),
                    "priority": (
                        matched_target.get("priority")
                        if matched_target
                        else None
                    ),
                    "status": (
                        matched_target.get("status")
                        if matched_target
                        else "active"
                    ),
                    "source": "blocking_prerequisite",
                }
            )

    # ---------------------------------------------------------
    # NORMAL TARGETED RETEST
    # ---------------------------------------------------------
    # If prerequisite repair is NOT active, preserve the existing
    # multi-target behavior.
    if not priority_concepts and retest_targets:
        seen_concepts: set[int] = set()

        for target in retest_targets:
            concept_id = target["concept_id"]

            if concept_id in seen_concepts:
                continue

            seen_concepts.add(concept_id)

            priority_concepts.append(
                {
                    "concept_id": concept_id,
                    "retest_target_id": target["id"],
                    "error_pattern_id": target[
                        "error_pattern_id"
                    ],
                    "reason": target["reason"],
                    "priority": target["priority"],
                    "status": target["status"],
                }
            )

    # ---------------------------------------------------------
    # WEAK-CONCEPT FALLBACK
    # ---------------------------------------------------------
    if not priority_concepts:
        if not snapshot["weak_concepts"]:
            return {
                "created": False,
                "reason": (
                    "No active retest targets or weak "
                    "concepts are currently available."
                ),
                "action": decision["action"],
                "priority_concepts": [],
                "questions": [],
                "question_count": 0,
                "session_id": None,
                "completed": False,
            }

        for concept in snapshot["weak_concepts"][:3]:
            priority_concepts.append(
                {
                    "concept_id": concept["concept_id"],
                    "graph_id": concept.get("graph_id"),
                    "mastery": concept.get("mastery"),
                    "status": concept.get("status"),
                    "source": "weak_concept_fallback",
                }
            )

    # ---------------------------------------------------------
    # QUESTION GENERATION
    # ---------------------------------------------------------
    all_questions: list[dict[str, Any]] = []

    for concept in priority_concepts:
        concept_id = concept["concept_id"]
        graph_id = concept.get("graph_id")

        if graph_id is None:
            for snapshot_concept in snapshot["weak_concepts"]:
                if (
                    snapshot_concept["concept_id"]
                    == concept_id
                ):
                    graph_id = snapshot_concept.get(
                        "graph_id"
                    )
                    break

        if graph_id is None:
            raise ValueError(
                f"No graph_id found for concept {concept_id}."
            )

        concept_questions = generate_questions_for_concept(
            graph_id=graph_id,
            concept_id=concept_id,
            topic=topic,
            subject=subject,
            academic_level=academic_level,
            count=questions_per_concept,
            difficulty=difficulty,
            cognitive_skill="conceptual_understanding",
            learner_summary=learner_summary,
        )

        all_questions.extend(concept_questions)

    if not all_questions:
        return {
            "created": False,
            "reason": "No questions were available for retest.",
            "action": decision["action"],
            "priority_concepts": priority_concepts,
            "questions": [],
            "question_count": 0,
            "session_id": None,
            "completed": False,
        }

    # ---------------------------------------------------------
    # SESSION VALIDATION
    # ---------------------------------------------------------
    graph_ids = {
        question["graph_id"]
        for question in all_questions
    }

    if len(graph_ids) != 1:
        raise ValueError(
            "A retest must use questions from one graph only."
        )

    graph_id = all_questions[0]["graph_id"]

    session_id = start_quiz_session(
        username=username,
        topic=topic,
        purpose="retest",
        difficulty=difficulty,
        question_count=len(all_questions),
        graph_id=graph_id,
    )

    # ---------------------------------------------------------
    # LINK REAL RETEST TARGETS
    # ---------------------------------------------------------
    linked_target_ids: list[int] = []

    for concept in priority_concepts:
        target_id = concept.get("retest_target_id")

        if target_id is None:
            continue

        link_retest_target_to_session(
            session_id=session_id,
            retest_target_id=target_id,
        )

        linked_target_ids.append(target_id)

    return {
        "created": True,
        "session_id": session_id,
        "username": username,
        "topic": topic,
        "subject": subject,
        "academic_level": academic_level,
        "purpose": "retest",
        "action": decision["action"],
        "reason": decision["reason"],
        "retest_targets": retest_targets,
        "linked_target_ids": linked_target_ids,
        "priority_concepts": priority_concepts,
        "questions": all_questions,
        "question_count": len(all_questions),
        "completed": False,
    }