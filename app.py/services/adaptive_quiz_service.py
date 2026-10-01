from typing import Any

from services.adaptive_question_service import (
    generate_adaptive_questions,
)
from services.quiz_session_service import (
    start_quiz_session,
)


VALID_PURPOSES = {
    "diagnostic",
    "practice",
    "retest",
    "revision",
}


def start_adaptive_quiz(
    username: str,
    graph_id: int,
    topic: str,
    subject: str,
    academic_level: str,
    count: int = 5,
    difficulty: str = "standard",
    cognitive_skill: str = "conceptual_understanding",
    purpose: str = "practice",
) -> dict[str, Any]:
    """
    Starts an adaptive quiz for a learner.

    Process:
    1. Reads learner state.
    2. Selects a target concept.
    3. Generates or reuses learner-aware questions.
    4. Creates a quiz session with the requested purpose.
    5. Returns the session and questions.

    Supported purposes:
    - diagnostic
    - practice
    - retest
    - revision
    """

    if count < 1:
        raise ValueError(
            "count must be at least 1"
        )

    purpose = purpose.strip().lower()

    if purpose not in VALID_PURPOSES:
        raise ValueError(
            "Invalid quiz purpose. "
            "Choose one of: diagnostic, practice, retest, revision."
        )

    adaptive_result = generate_adaptive_questions(
        username=username,
        graph_id=graph_id,
        topic=topic,
        subject=subject,
        academic_level=academic_level,
        count=count,
        difficulty=difficulty,
        cognitive_skill=cognitive_skill,
    )

    if not adaptive_result["created"]:
        return {
            "created": False,
            "username": username,
            "purpose": purpose,
            "reason": adaptive_result.get("reason"),
            "recommended_action": adaptive_result.get(
                "recommended_action"
            ),
            "session_id": None,
            "questions": [],
            "question_count": 0,
            "completed": False,
        }

    questions = adaptive_result["questions"]

    session_id = start_quiz_session(
        username=username,
        topic=topic,
        purpose=purpose,
        difficulty=difficulty,
        question_count=len(questions),
        graph_id=graph_id,
    )

    return {
        "created": True,
        "username": username,
        "session_id": session_id,
        "purpose": purpose,
        "recommended_action": adaptive_result.get(
            "recommended_action"
        ),
        "adaptation_reason": adaptive_result.get(
            "adaptation_reason"
        ),
        "target_reason": adaptive_result.get(
            "target_reason"
        ),
        "target_concept": adaptive_result.get(
            "target_concept"
        ),
        "questions": questions,
        "question_count": len(questions),
        "completed": False,
    }