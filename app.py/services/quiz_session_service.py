from typing import Any

from utils.database import get_connection


def _ensure_retest_mapping_table() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS retest_session_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                retest_target_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_id, retest_target_id),
                FOREIGN KEY(session_id)
                    REFERENCES quiz_sessions(id)
                    ON DELETE CASCADE,
                FOREIGN KEY(retest_target_id)
                    REFERENCES retest_targets(id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _ensure_session_questions_table() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_session_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                question_order INTEGER NOT NULL,
                answered INTEGER NOT NULL DEFAULT 0,
                answered_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_id, question_id),
                FOREIGN KEY(session_id)
                    REFERENCES quiz_sessions(id)
                    ON DELETE CASCADE,
                FOREIGN KEY(question_id)
                    REFERENCES questions(id)
                    ON DELETE CASCADE
            )
            """
        )

        columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(quiz_session_questions)"
            ).fetchall()
        }

        if "answered" not in columns:
            conn.execute(
                """
                ALTER TABLE quiz_session_questions
                ADD COLUMN answered INTEGER NOT NULL DEFAULT 0
                """
            )

        if "answered_at" not in columns:
            conn.execute(
                """
                ALTER TABLE quiz_session_questions
                ADD COLUMN answered_at TIMESTAMP
                """
            )

        conn.commit()
    finally:
        conn.close()


def start_quiz_session(
    username: str,
    topic: str,
    purpose: str,
    difficulty: str,
    question_count: int,
    graph_id: int | None = None,
) -> int:
    if not username:
        raise ValueError("username is required")

    if not topic:
        raise ValueError("topic is required")

    if question_count < 1:
        raise ValueError("question_count must be at least 1")

    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO quiz_sessions (
                username,
                topic,
                graph_id,
                purpose,
                difficulty,
                question_count,
                completed
            )
            VALUES (?, ?, ?, ?, ?, ?, 0)
            """,
            (
                username,
                topic,
                graph_id,
                purpose,
                difficulty,
                question_count,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()


def save_session_questions(
    session_id: int,
    question_ids: list[int],
) -> None:
    _ensure_session_questions_table()

    if not question_ids:
        raise ValueError("question_ids cannot be empty")

    conn = get_connection()
    try:
        for order, question_id in enumerate(question_ids, start=1):
            conn.execute(
                """
                INSERT OR IGNORE INTO quiz_session_questions (
                    session_id,
                    question_id,
                    question_order,
                    answered,
                    answered_at
                )
                VALUES (?, ?, ?, 0, NULL)
                """,
                (
                    session_id,
                    question_id,
                    order,
                ),
            )

        conn.commit()
    finally:
        conn.close()


def get_session_question_ids(
    session_id: int,
) -> list[int]:
    _ensure_session_questions_table()

    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT question_id
            FROM quiz_session_questions
            WHERE session_id = ?
            ORDER BY question_order ASC
            """,
            (session_id,),
        ).fetchall()

        return [
            int(row["question_id"])
            for row in rows
        ]
    finally:
        conn.close()


def is_session_question_answered(
    session_id: int,
    question_id: int,
) -> bool:
    _ensure_session_questions_table()

    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT answered
            FROM quiz_session_questions
            WHERE session_id = ?
              AND question_id = ?
            """,
            (
                session_id,
                question_id,
            ),
        ).fetchone()

        if row is None:
            return False

        return bool(row["answered"])
    finally:
        conn.close()


def mark_session_question_answered(
    session_id: int,
    question_id: int,
) -> bool:
    _ensure_session_questions_table()

    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE quiz_session_questions
            SET answered = 1,
                answered_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
              AND question_id = ?
              AND answered = 0
            """,
            (
                session_id,
                question_id,
            ),
        )

        conn.commit()

        return cursor.rowcount > 0
    finally:
        conn.close()


def get_session_progress(
    session_id: int,
) -> dict[str, int | float | bool]:
    """
    Returns question-level progress for a quiz session.
    """

    _ensure_session_questions_table()

    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS total_questions,
                SUM(
                    CASE
                        WHEN answered = 1 THEN 1
                        ELSE 0
                    END
                ) AS answered_questions
            FROM quiz_session_questions
            WHERE session_id = ?
            """,
            (session_id,),
        ).fetchone()

        if row is None:
            return {
                "total_questions": 0,
                "answered_questions": 0,
                "remaining_questions": 0,
                "progress": 0.0,
                "complete": False,
            }

        total = int(row["total_questions"] or 0)
        answered = int(row["answered_questions"] or 0)
        remaining = max(0, total - answered)

        progress = (
            answered / total
            if total > 0
            else 0.0
        )

        return {
            "total_questions": total,
            "answered_questions": answered,
            "remaining_questions": remaining,
            "progress": progress,
            "complete": (
                total > 0
                and answered == total
            ),
        }
    finally:
        conn.close()


def link_retest_target_to_session(
    session_id: int,
    retest_target_id: int,
) -> None:
    _ensure_retest_mapping_table()

    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT OR IGNORE INTO retest_session_targets (
                session_id,
                retest_target_id
            )
            VALUES (?, ?)
            """,
            (
                session_id,
                retest_target_id,
            ),
        )

        conn.commit()
    finally:
        conn.close()


def get_retest_targets_for_session(
    session_id: int,
) -> list[dict[str, Any]]:
    _ensure_retest_mapping_table()

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
            FROM retest_session_targets AS rsm
            JOIN retest_targets AS rt
                ON rt.id = rsm.retest_target_id
            JOIN concepts AS c
                ON c.id = rt.concept_id
            WHERE rsm.session_id = ?
            ORDER BY rt.priority DESC, rt.created_at ASC
            """,
            (session_id,),
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_retest_targets_for_session_concept(
    session_id: int,
    concept_id: int,
) -> list[dict[str, Any]]:
    _ensure_retest_mapping_table()

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
            FROM retest_session_targets AS rsm
            JOIN retest_targets AS rt
                ON rt.id = rsm.retest_target_id
            JOIN concepts AS c
                ON c.id = rt.concept_id
            WHERE rsm.session_id = ?
              AND rt.concept_id = ?
            ORDER BY rt.priority DESC, rt.created_at ASC
            """,
            (
                session_id,
                concept_id,
            ),
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_quiz_session(
    session_id: int,
) -> dict[str, Any] | None:
    conn = get_connection()
    try:
        row = conn.execute(
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

        return dict(row) if row else None
    finally:
        conn.close()


def get_user_quiz_sessions(
    username: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute(
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
            WHERE username = ?
            ORDER BY created_at DESC
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


def complete_quiz_session(
    session_id: int,
) -> bool:
    """
    Completes a quiz only when every assigned
    session question has been answered.
    """

    session = get_quiz_session(session_id)

    if session is None:
        raise ValueError("Quiz session not found.")

    if session["completed"]:
        return False

    progress = get_session_progress(session_id)

    if progress["total_questions"] == 0:
        raise ValueError(
            "Quiz session has no assigned questions."
        )

    if not progress["complete"]:
        raise ValueError(
            "Quiz cannot be completed yet. "
            f"{progress['remaining_questions']} "
            "question(s) remain unanswered."
        )

    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE quiz_sessions
            SET completed = 1,
                completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
              AND completed = 0
            """,
            (session_id,),
        )

        conn.commit()

        return cursor.rowcount > 0
    finally:
        conn.close()


def is_quiz_session_completed(
    session_id: int,
) -> bool:
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT completed
            FROM quiz_sessions
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()

        if row is None:
            raise ValueError("Quiz session not found.")

        return bool(row["completed"])
    finally:
        conn.close()