import json
from typing import Any, Optional

from utils.database import get_connection


ALLOWED_QUESTION_TYPES = {
    "mcq",
    "short_answer",
    "numerical",
    "true_false",
    "conceptual",
    "application",
    "reasoning",
}


ALLOWED_SKILLS = {
    "memory",
    "conceptual_understanding",
    "logical_thinking",
    "application",
    "pattern_recognition",
}


ALLOWED_DIFFICULTIES = {
    "basic",
    "standard",
    "advanced",
}


def validate_question_data(
    question_data: dict[str, Any],
) -> None:
    """
    Validates one AI-generated question.
    """

    if not isinstance(question_data, dict):
        raise ValueError("question_data must be a dictionary")

    required_fields = [
        "question_key",
        "question_text",
        "question_type",
        "cognitive_skill",
        "difficulty",
        "expected_answer",
        "explanation",
    ]

    for field in required_fields:
        if field not in question_data:
            raise ValueError(
                f"Missing required question field: {field}"
            )

    if not isinstance(question_data["question_key"], str):
        raise ValueError("question_key must be a string")

    if not question_data["question_key"].strip():
        raise ValueError("question_key cannot be empty")

    if not isinstance(question_data["question_text"], str):
        raise ValueError("question_text must be a string")

    if not question_data["question_text"].strip():
        raise ValueError("question_text cannot be empty")

    if question_data["question_type"] not in ALLOWED_QUESTION_TYPES:
        raise ValueError(
            f"Invalid question_type: "
            f"{question_data['question_type']}"
        )

    if question_data["cognitive_skill"] not in ALLOWED_SKILLS:
        raise ValueError(
            f"Invalid cognitive_skill: "
            f"{question_data['cognitive_skill']}"
        )

    if question_data["difficulty"] not in ALLOWED_DIFFICULTIES:
        raise ValueError(
            f"Invalid difficulty: "
            f"{question_data['difficulty']}"
        )

    if not str(question_data["expected_answer"]).strip():
        raise ValueError("expected_answer cannot be empty")

    if not str(question_data["explanation"]).strip():
        raise ValueError("explanation cannot be empty")


def concept_exists(
    graph_id: int,
    concept_id: int,
) -> bool:
    """
    Checks whether a concept belongs to the specified graph.
    """

    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT id
            FROM concepts
            WHERE id = ?
              AND graph_id = ?
            """,
            (concept_id, graph_id),
        ).fetchone()

        return row is not None

    finally:
        conn.close()


def save_question(
    question_data: dict[str, Any],
    graph_id: int,
    concept_id: int,
    generation_source: str = "ai",
) -> int:
    """
    Validates and saves one question.

    Returns:
        question_id
    """

    validate_question_data(question_data)

    if not concept_exists(graph_id, concept_id):
        raise ValueError(
            "The selected concept does not belong to this graph"
        )

    conn = get_connection()

    try:
        existing = conn.execute(
            """
            SELECT id
            FROM questions
            WHERE question_key = ?
            """,
            (question_data["question_key"],),
        ).fetchone()

        if existing is not None:
            raise ValueError(
                "Question already exists: "
                f"{question_data['question_key']}"
            )

        cursor = conn.execute(
            """
            INSERT INTO questions (
                question_key,
                graph_id,
                concept_id,
                question_text,
                question_type,
                cognitive_skill,
                difficulty,
                answer_format,
                expected_answer,
                explanation,
                possible_error_types,
                prerequisite_concepts,
                validation_status,
                generation_source,
                metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                question_data["question_key"],
                graph_id,
                concept_id,
                question_data["question_text"],
                question_data["question_type"],
                question_data["cognitive_skill"],
                question_data["difficulty"],
                question_data.get("answer_format", "text"),
                str(question_data["expected_answer"]),
                str(question_data["explanation"]),
                json.dumps(
                    question_data.get("possible_error_types", [])
                ),
                json.dumps(
                    question_data.get("prerequisite_concepts", [])
                ),
                "validated",
                generation_source,
                json.dumps(
                    question_data.get("metadata", {})
                ),
            ),
        )

        conn.commit()

        return cursor.lastrowid

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_question(question_id: int) -> Optional[dict[str, Any]]:
    """
    Loads one question by ID.
    """

    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT *
            FROM questions
            WHERE id = ?
            """,
            (question_id,),
        ).fetchone()

        if row is None:
            return None

        question = dict(row)

        question["possible_error_types"] = json.loads(
            question["possible_error_types"] or "[]"
        )

        question["prerequisite_concepts"] = json.loads(
            question["prerequisite_concepts"] or "[]"
        )

        question["metadata"] = json.loads(
            question["metadata"] or "{}"
        )

        return question

    finally:
        conn.close()


def get_questions_for_graph(
    graph_id: int,
    concept_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    cognitive_skill: Optional[str] = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """
    Retrieves questions using graph/concept/skill filters.
    """

    if limit < 1:
        raise ValueError("limit must be at least 1")

    filters = ["graph_id = ?", "validation_status = 'validated'"]
    parameters: list[Any] = [graph_id]

    if concept_id is not None:
        filters.append("concept_id = ?")
        parameters.append(concept_id)

    if difficulty is not None:
        if difficulty not in ALLOWED_DIFFICULTIES:
            raise ValueError("Invalid difficulty")

        filters.append("difficulty = ?")
        parameters.append(difficulty)

    if cognitive_skill is not None:
        if cognitive_skill not in ALLOWED_SKILLS:
            raise ValueError("Invalid cognitive_skill")

        filters.append("cognitive_skill = ?")
        parameters.append(cognitive_skill)

    parameters.append(limit)

    query = f"""
        SELECT *
        FROM questions
        WHERE {' AND '.join(filters)}
        ORDER BY id
        LIMIT ?
    """

    conn = get_connection()

    try:
        rows = conn.execute(query, parameters).fetchall()

        questions = []

        for row in rows:
            question = dict(row)

            question["possible_error_types"] = json.loads(
                question["possible_error_types"] or "[]"
            )

            question["prerequisite_concepts"] = json.loads(
                question["prerequisite_concepts"] or "[]"
            )

            question["metadata"] = json.loads(
                question["metadata"] or "{}"
            )

            questions.append(question)

        return questions

    finally:
        conn.close()