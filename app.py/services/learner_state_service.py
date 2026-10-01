from typing import Any, Optional

from utils.database import get_connection

from modeles.learner_state import (
    ConceptState,
    ErrorPattern,
    LearnerState,
    SkillState,
)


DEFAULT_SKILLS = [
    "memory",
    "conceptual_understanding",
    "logical_thinking",
    "application",
    "pattern_recognition",
]


def create_empty_learner_state(username: str) -> LearnerState:
    """
    Creates a learner state with default skill categories.
    """
    learner_state = LearnerState(username=username)

    for skill_key in DEFAULT_SKILLS:
        learner_state.get_or_create_skill_state(skill_key)

    return learner_state


def load_learner_state(username: str) -> LearnerState:
    """
    Loads learner data from SQLite.

    If the learner has no previous evidence,
    returns a fresh learner state.
    """
    learner_state = create_empty_learner_state(username)

    conn = get_connection()

    try:
        concept_rows = conn.execute(
            """
            SELECT
                username,
                concept_id,
                mastery,
                confidence,
                evidence_count,
                recent_accuracy,
                trend,
                status,
                last_evidence_at
            FROM learner_concept_state
            WHERE username = ?
            """,
            (username,),
        ).fetchall()

        for row in concept_rows:
            state = ConceptState(
                concept_id=row["concept_id"],
                username=row["username"],
                mastery=row["mastery"],
                confidence=row["confidence"],
                evidence_count=row["evidence_count"],
                recent_accuracy=row["recent_accuracy"],
                trend=row["trend"],
                status=row["status"],
                last_evidence_at=row["last_evidence_at"],
            )

            learner_state.concept_states[state.concept_id] = state

        skill_rows = conn.execute(
            """
            SELECT
                username,
                skill_key,
                estimate,
                confidence,
                evidence_count,
                recent_accuracy,
                trend
            FROM learner_skill_state
            WHERE username = ?
            """,
            (username,),
        ).fetchall()

        for row in skill_rows:
            state = SkillState(
                username=row["username"],
                skill_key=row["skill_key"],
                estimate=row["estimate"],
                confidence=row["confidence"],
                evidence_count=row["evidence_count"],
                recent_accuracy=row["recent_accuracy"],
                trend=row["trend"],
            )

            learner_state.skill_states[state.skill_key] = state

        error_rows = conn.execute(
            """
            SELECT
                username,
                pattern_key,
                category,
                description,
                concept_id,
                occurrences,
                confidence,
                status
            FROM learner_error_patterns
            WHERE username = ?
            """,
            (username,),
        ).fetchall()

        for row in error_rows:
            pattern = ErrorPattern(
                username=row["username"],
                pattern_key=row["pattern_key"],
                category=row["category"],
                description=row["description"],
                concept_id=row["concept_id"],
                occurrences=row["occurrences"],
                confidence=row["confidence"],
                status=row["status"],
            )

            learner_state.error_patterns[pattern.pattern_key] = pattern

        return learner_state

    finally:
        conn.close()


def save_concept_state(state: ConceptState) -> None:
    """
    Saves or updates one concept's learner state.
    """
    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO learner_concept_state (
                username,
                concept_id,
                mastery,
                confidence,
                evidence_count,
                recent_accuracy,
                trend,
                status,
                last_evidence_at,
                updated_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT(username, concept_id)
            DO UPDATE SET
                mastery = excluded.mastery,
                confidence = excluded.confidence,
                evidence_count = excluded.evidence_count,
                recent_accuracy = excluded.recent_accuracy,
                trend = excluded.trend,
                status = excluded.status,
                last_evidence_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                state.username,
                state.concept_id,
                state.mastery,
                state.confidence,
                state.evidence_count,
                state.recent_accuracy,
                state.trend,
                state.status,
            ),
        )

        conn.commit()

    finally:
        conn.close()


def save_skill_state(state: SkillState) -> None:
    """
    Saves or updates one skill's learner state.
    """
    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO learner_skill_state (
                username,
                skill_key,
                estimate,
                confidence,
                evidence_count,
                recent_accuracy,
                trend,
                updated_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT(username, skill_key)
            DO UPDATE SET
                estimate = excluded.estimate,
                confidence = excluded.confidence,
                evidence_count = excluded.evidence_count,
                recent_accuracy = excluded.recent_accuracy,
                trend = excluded.trend,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                state.username,
                state.skill_key,
                state.estimate,
                state.confidence,
                state.evidence_count,
                state.recent_accuracy,
                state.trend,
            ),
        )

        conn.commit()

    finally:
        conn.close()


def save_error_pattern(pattern: ErrorPattern) -> None:
    """
    Saves or updates one recurring error pattern.
    """
    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO learner_error_patterns (
                username,
                concept_id,
                pattern_key,
                category,
                description,
                occurrences,
                confidence,
                status,
                first_seen_at,
                last_seen_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT(username, pattern_key)
            DO UPDATE SET
                concept_id = excluded.concept_id,
                category = excluded.category,
                description = excluded.description,
                occurrences = excluded.occurrences,
                confidence = excluded.confidence,
                status = excluded.status,
                last_seen_at = CURRENT_TIMESTAMP
            """,
            (
                pattern.username,
                pattern.concept_id,
                pattern.pattern_key,
                pattern.category,
                pattern.description,
                pattern.occurrences,
                pattern.confidence,
                pattern.status,
            ),
        )

        conn.commit()

    finally:
        conn.close()


def save_quiz_evidence(
    username: str,
    session_id: int,
    question_id: int,
    concept_id: int,
    result: str,
    student_answer: str,
    correct_answer: str,
    question_type: str,
    cognitive_skill: str,
    difficulty: str,
    error_category: Optional[str] = None,
    diagnosis_confidence: float = 0.0,
    used_hint: bool = False,
    response_time_seconds: Optional[float] = None,
    evaluator_notes: Optional[str] = None,
) -> int:
    """
    Saves one raw quiz evidence record.

    Returns:
        Newly created evidence ID.
    """
    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO quiz_evidence (
                username,
                session_id,
                question_id,
                concept_id,
                result,
                student_answer,
                correct_answer,
                question_type,
                cognitive_skill,
                difficulty,
                error_category,
                diagnosis_confidence,
                used_hint,
                response_time_seconds,
                evaluator_notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                session_id,
                question_id,
                concept_id,
                result,
                student_answer,
                correct_answer,
                question_type,
                cognitive_skill,
                difficulty,
                error_category,
                diagnosis_confidence,
                int(used_hint),
                response_time_seconds,
                evaluator_notes,
            ),
        )

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def create_retest_target(
    username: str,
    concept_id: int,
    pattern_key: str,
    reason: str,
    priority: int = 1,
) -> Optional[int]:
    """
    Creates an active retest target for a diagnosed error pattern.

    If an active target already exists for the same
    learner, concept and error pattern, it is not duplicated.

    Returns:
        Retest target ID if created or already active.

        None if the corresponding error pattern cannot be found.
    """
    conn = get_connection()

    try:
        pattern_row = conn.execute(
            """
            SELECT id
            FROM learner_error_patterns
            WHERE username = ?
              AND pattern_key = ?
            """,
            (
                username,
                pattern_key,
            ),
        ).fetchone()

        if pattern_row is None:
            return None

        error_pattern_id = pattern_row["id"]

        existing_row = conn.execute(
            """
            SELECT id
            FROM retest_targets
            WHERE username = ?
              AND concept_id = ?
              AND error_pattern_id = ?
              AND status = 'active'
            LIMIT 1
            """,
            (
                username,
                concept_id,
                error_pattern_id,
            ),
        ).fetchone()

        if existing_row is not None:
            return existing_row["id"]

        cursor = conn.execute(
            """
            INSERT INTO retest_targets (
                username,
                concept_id,
                error_pattern_id,
                reason,
                priority,
                status,
                created_at
            )
            VALUES (
                ?, ?, ?, ?, ?, 'active',
                CURRENT_TIMESTAMP
            )
            """,
            (
                username,
                concept_id,
                error_pattern_id,
                reason,
                priority,
            ),
        )

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def record_quiz_result(
    username: str,
    session_id: int,
    question_id: int,
    concept_id: int,
    result: str,
    student_answer: str,
    correct_answer: str,
    question_type: str,
    cognitive_skill: str,
    difficulty: str,
    error_category: Optional[str] = None,
    error_pattern_key: Optional[str] = None,
    error_description: Optional[str] = None,
    diagnosis_confidence: float = 0.0,
    used_hint: bool = False,
    response_time_seconds: Optional[float] = None,
    evaluator_notes: Optional[str] = None,
) -> LearnerState:
    """
    Main public function.

    Records one quiz answer and updates the learner model.

    Flow:

        Quiz evidence
              ↓
        Learner state
              ↓
        Error pattern
              ↓
        Retest target
    """

    if result not in {
        "correct",
        "incorrect",
        "partial",
        "skipped",
    }:
        raise ValueError(
            "result must be: correct, incorrect, partial, or skipped"
        )

    if not username.strip():
        raise ValueError("username cannot be empty")

    if not cognitive_skill.strip():
        raise ValueError("cognitive_skill cannot be empty")

    diagnosis_confidence = max(
        0.0,
        min(1.0, float(diagnosis_confidence)),
    )

    is_correct = result == "correct"

    # ---------------------------------------------------------
    # 1. Save raw quiz evidence.
    # ---------------------------------------------------------

    save_quiz_evidence(
        username=username,
        session_id=session_id,
        question_id=question_id,
        concept_id=concept_id,
        result=result,
        student_answer=student_answer,
        correct_answer=correct_answer,
        question_type=question_type,
        cognitive_skill=cognitive_skill,
        difficulty=difficulty,
        error_category=error_category,
        diagnosis_confidence=diagnosis_confidence,
        used_hint=used_hint,
        response_time_seconds=response_time_seconds,
        evaluator_notes=evaluator_notes,
    )

    # ---------------------------------------------------------
    # 2. Load current learner state.
    # ---------------------------------------------------------

    learner_state = load_learner_state(username)

    # ---------------------------------------------------------
    # 3. Update concept and skill state.
    # ---------------------------------------------------------

    learner_state.record_evidence(
        concept_id=concept_id,
        skill_key=cognitive_skill,
        correct=is_correct,
        evidence_data={
            "session_id": session_id,
            "question_id": question_id,
            "result": result,
            "difficulty": difficulty,
            "diagnosis_confidence": diagnosis_confidence,
        },
    )

    # ---------------------------------------------------------
    # 4. Record diagnosed error.
    # ---------------------------------------------------------

    if (
        result in {"incorrect", "partial"}
        and error_category
        and error_pattern_key
        and error_description
    ):
        learner_state.add_error_pattern(
            pattern_key=error_pattern_key,
            category=error_category,
            description=error_description,
            concept_id=concept_id,
        )

    # ---------------------------------------------------------
    # 5. Persist concept state.
    # ---------------------------------------------------------

    concept_state = learner_state.concept_states[concept_id]

    save_concept_state(concept_state)

    # ---------------------------------------------------------
    # 6. Persist skill state.
    # ---------------------------------------------------------

    skill_state = learner_state.skill_states[cognitive_skill]

    save_skill_state(skill_state)

    # ---------------------------------------------------------
    # 7. Persist error pattern.
    # ---------------------------------------------------------

    if error_pattern_key in learner_state.error_patterns:
        pattern = learner_state.error_patterns[error_pattern_key]

        save_error_pattern(pattern)

        # -----------------------------------------------------
        # 8. Create retest target.
        # -----------------------------------------------------

        if result in {"incorrect", "partial"}:
            priority = 1

            if concept_state.mastery < 0.30:
                priority = 3
            elif concept_state.mastery < 0.50:
                priority = 2

            retest_reason = (
                f"Retest concept {concept_id} because the learner "
                f"showed a {pattern.category} error: "
                f"{pattern.description}"
            )

            create_retest_target(
                username=username,
                concept_id=concept_id,
                pattern_key=error_pattern_key,
                reason=retest_reason,
                priority=priority,
            )

    return learner_state


def get_retest_targets(
    username: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Returns the learner's active retest targets.

    Also returns graph_id for the target concept so the
    retest service can generate questions from the correct graph.
    """

    if limit < 1:
        raise ValueError("limit must be at least 1")

    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                rt.id,
                rt.username,
                rt.concept_id,
                c.graph_id,
                rt.error_pattern_id,
                rt.reason,
                rt.priority,
                rt.status,
                rt.created_at
            FROM retest_targets AS rt
            JOIN concepts AS c
                ON c.id = rt.concept_id
            WHERE rt.username = ?
              AND rt.status = 'active'
            ORDER BY rt.priority DESC, rt.created_at ASC
            LIMIT ?
            """,
            (
                username,
                limit,
            ),
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


def complete_retest_target(
    username: str,
    target_id: int,
) -> bool:
    """
    Marks an active retest target as resolved.

    Returns:
        True  -> target was successfully resolved.
        False -> target did not exist, belonged to another
                 learner, or was already resolved.
    """

    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            UPDATE retest_targets
            SET status = 'resolved'
            WHERE id = ?
              AND username = ?
              AND status = 'active'
            """,
            (
                target_id,
                username,
            ),
        )

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()


def get_learner_summary(username: str) -> dict[str, Any]:
    """
    Creates a compact learner summary for the adaptive planner.
    """

    learner_state = load_learner_state(username)

    weak_concepts = sorted(
        learner_state.get_weak_concepts(),
        key=lambda state: state.mastery,
    )

    skill_summary = {
        skill_key: {
            "estimate": round(state.estimate, 3),
            "confidence": round(state.confidence, 3),
            "evidence_count": state.evidence_count,
            "recent_accuracy": round(state.recent_accuracy, 3),
            "trend": state.trend,
        }
        for skill_key, state in learner_state.skill_states.items()
    }

    error_summary = [
        {
            "pattern_key": pattern.pattern_key,
            "category": pattern.category,
            "description": pattern.description,
            "concept_id": pattern.concept_id,
            "occurrences": pattern.occurrences,
            "confidence": round(pattern.confidence, 3),
        }
        for pattern in learner_state.get_priority_error_patterns()
    ]

    conn = get_connection()

    try:
        evidence_row = conn.execute(
            """
            SELECT COUNT(*) AS evidence_count
            FROM quiz_evidence
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

        recent_evidence_count = int(
            evidence_row["evidence_count"] or 0
        )

    finally:
        conn.close()

    return {
        "username": username,
        "weak_concepts": [
            {
                "concept_id": state.concept_id,
                "mastery": round(state.mastery, 3),
                "confidence": round(state.confidence, 3),
                "status": state.status,
                "trend": state.trend,
                "evidence_count": state.evidence_count,
            }
            for state in weak_concepts
        ],
        "skills": skill_summary,
        "error_patterns": error_summary,
        "recent_evidence_count": recent_evidence_count,
    }


def get_quiz_result_summary(
    session_id: int,
) -> dict[str, Any]:
    """
    Creates a persistent result summary for one quiz session.

    The summary is calculated from quiz_evidence and the
    session's assigned questions.

    This function does not modify learner state.
    """

    conn = get_connection()

    try:
        session_row = conn.execute(
            """
            SELECT
                id,
                username,
                topic,
                graph_id,
                purpose,
                difficulty,
                question_count,
                completed,
                created_at,
                completed_at
            FROM quiz_sessions
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()

        if session_row is None:
            raise ValueError(
                "Quiz session not found."
            )

        session = dict(session_row)

        evidence_rows = conn.execute(
            """
            SELECT
                qe.id,
                qe.question_id,
                qe.concept_id,
                qe.result,
                qe.error_category,
                qe.diagnosis_confidence,
                qe.used_hint,
                qe.response_time_seconds,
                c.name AS concept_name
            FROM quiz_evidence AS qe
            LEFT JOIN concepts AS c
                ON c.id = qe.concept_id
            WHERE qe.session_id = ?
            ORDER BY qe.id ASC
            """,
            (session_id,),
        ).fetchall()

        result_counts = {
            "correct": 0,
            "incorrect": 0,
            "partial": 0,
            "skipped": 0,
        }

        concept_map: dict[int, dict[str, Any]] = {}
        error_map: dict[str, dict[str, Any]] = {}

        total_response_time = 0.0
        response_time_count = 0

        for row in evidence_rows:
            result = row["result"]

            if result in result_counts:
                result_counts[result] += 1

            concept_id = row["concept_id"]

            if concept_id is not None:
                if concept_id not in concept_map:
                    concept_map[concept_id] = {
                        "concept_id": concept_id,
                        "concept_name": row["concept_name"],
                        "attempts": 0,
                        "correct": 0,
                        "incorrect": 0,
                        "partial": 0,
                        "skipped": 0,
                    }

                concept_data = concept_map[concept_id]

                concept_data["attempts"] += 1

                if result in {
                    "correct",
                    "incorrect",
                    "partial",
                    "skipped",
                }:
                    concept_data[result] += 1

            error_category = row["error_category"]

            if error_category:
                if error_category not in error_map:
                    error_map[error_category] = {
                        "category": error_category,
                        "occurrences": 0,
                        "average_confidence": 0.0,
                    }

                error_map[error_category]["occurrences"] += 1
                error_map[error_category][
                    "average_confidence"
                ] += float(
                    row["diagnosis_confidence"] or 0.0
                )

            if row["response_time_seconds"] is not None:
                total_response_time += float(
                    row["response_time_seconds"]
                )
                response_time_count += 1

        for error_data in error_map.values():
            occurrences = error_data["occurrences"]

            if occurrences > 0:
                error_data["average_confidence"] = round(
                    error_data["average_confidence"]
                    / occurrences,
                    3,
                )

        answered = len(evidence_rows)
        total_questions = int(
            session["question_count"] or 0
        )

        accuracy = (
            result_counts["correct"] / answered
            if answered > 0
            else 0.0
        )

        progress = (
            answered / total_questions
            if total_questions > 0
            else 0.0
        )

        retest_rows = conn.execute(
            """
            SELECT DISTINCT
                rt.id,
                rt.concept_id,
                c.name AS concept_name,
                rt.error_pattern_id,
                rt.reason,
                rt.priority,
                rt.status
            FROM retest_targets AS rt
            JOIN concepts AS c
                ON c.id = rt.concept_id
            JOIN learner_error_patterns AS lep
                ON lep.id = rt.error_pattern_id
            JOIN quiz_evidence AS qe
                ON qe.username = rt.username
               AND qe.concept_id = rt.concept_id
               AND qe.session_id = ?
               AND lep.pattern_key = (
                   SELECT pattern_key
                   FROM learner_error_patterns
                   WHERE id = rt.error_pattern_id
               )
            WHERE rt.username = ?
            ORDER BY rt.priority DESC, rt.id ASC
            """,
            (
                session["id"],
                session["username"],
            ),
        ).fetchall()

        retest_targets = [
            dict(row)
            for row in retest_rows
        ]

        return {
            "session_id": session["id"],
            "username": session["username"],
            "topic": session["topic"],
            "graph_id": session["graph_id"],
            "purpose": session["purpose"],
            "difficulty": session["difficulty"],
            "completed": bool(session["completed"]),
            "total_questions": total_questions,
            "answered_questions": answered,
            "remaining_questions": max(
                0,
                total_questions - answered,
            ),
            "progress": round(progress, 3),
            "result_counts": result_counts,
            "accuracy": round(accuracy, 3),
            "concepts_tested": list(
                concept_map.values()
            ),
            "error_patterns": list(
                error_map.values()
            ),
            "retest_targets": retest_targets,
            "average_response_time_seconds": (
                round(
                    total_response_time
                    / response_time_count,
                    3,
                )
                if response_time_count > 0
                else None
            ),
            "created_at": session["created_at"],
            "completed_at": session["completed_at"],
        }

    finally:
        conn.close()