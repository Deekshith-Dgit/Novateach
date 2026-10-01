from typing import Any, Optional

from services.adaptation_service import (
    choose_next_action,
    get_learner_snapshot,
)

from services.question_generation_service import (
    generate_questions_for_concept,
)


def get_concept_id(
    concept: dict[str, Any],
) -> Optional[int]:
    """
    Extracts the concept ID safely.

    Different database queries may return the ID with
    different names, such as:
    - id
    - concept_id
    """

    concept_id = concept.get("id")

    if concept_id is None:
        concept_id = concept.get("concept_id")

    if concept_id is None:
        return None

    return int(concept_id)


def select_target_concept(
    username: str,
    graph_id: int | None = None,
) -> dict[str, Any]:
    """
    Selects the next concept that needs learning support.

    Priority:
    1. Weak concepts
    2. Concepts belonging to the requested graph
    3. First available concept
    """

    snapshot = get_learner_snapshot(username)

    weak_concepts = snapshot.get(
        "weak_concepts",
        [],
    )

    if graph_id is not None:
        weak_concepts = [
            concept
            for concept in weak_concepts
            if concept.get("graph_id") == graph_id
        ]

    if weak_concepts:
        selected = weak_concepts[0]

        return {
            "selected": True,
            "reason": "weak_concept",
            "concept": selected,
        }

    all_concepts = snapshot.get(
        "all_concepts",
        [],
    )

    if graph_id is not None:
        all_concepts = [
            concept
            for concept in all_concepts
            if concept.get("graph_id") == graph_id
        ]

    if all_concepts:
        selected = all_concepts[0]

        return {
            "selected": True,
            "reason": "next_available_concept",
            "concept": selected,
        }

    return {
        "selected": False,
        "reason": "no_concept_available",
        "concept": None,
    }


def generate_adaptive_questions(
    username: str,
    graph_id: int,
    topic: str,
    subject: str,
    academic_level: str,
    count: int = 5,
    difficulty: str = "standard",
    cognitive_skill: str = "conceptual_understanding",
) -> dict[str, Any]:
    """
    Generates questions based on the learner's current state.

    Process:

        Learner state
             ↓
        Adaptation decision
             ↓
        Target concept selection
             ↓
        Prerequisite check
             ↓
        Learner-aware question generation
    """

    if count < 1:
        raise ValueError(
            "count must be at least 1"
        )

    # --------------------------------------------------
    # 1. Ask the adaptation engine what should happen
    # --------------------------------------------------

    decision = choose_next_action(username)

    action = decision.get("action")

    # --------------------------------------------------
    # 2. Normal target selection
    # --------------------------------------------------

    target = select_target_concept(
        username=username,
        graph_id=graph_id,
    )

    if not target["selected"]:
        return {
            "created": False,
            "username": username,
            "reason": target["reason"],
            "recommended_action": action,
            "questions": [],
            "question_count": 0,
        }

    concept = target["concept"]

    # --------------------------------------------------
    # 3. Prerequisite repair override
    # --------------------------------------------------
    #
    # Example:
    #
    # Electric Charge
    #       ↓
    # Electric Field
    #
    # If Electric Field is the target but Electric
    # Charge is weak, adaptation_service returns:
    #
    # action = prerequisite_repair
    # blocking_prerequisite = Electric Charge
    #
    # In that case we generate questions for Electric
    # Charge instead of Electric Field.
    # --------------------------------------------------

    blocking_prerequisite = decision.get(
        "blocking_prerequisite"
    )

    if (
        action == "prerequisite_repair"
        and blocking_prerequisite is not None
    ):
        prerequisite_graph_id = (
            blocking_prerequisite.get("graph_id")
        )

        if (
            prerequisite_graph_id is not None
            and int(prerequisite_graph_id) != int(graph_id)
        ):
            return {
                "created": False,
                "username": username,
                "reason": (
                    "Blocking prerequisite belongs "
                    "to a different knowledge graph."
                ),
                "recommended_action": action,
                "questions": [],
                "question_count": 0,
                "target_concept": concept,
                "blocking_prerequisite": (
                    blocking_prerequisite
                ),
            }

        concept = blocking_prerequisite

        target_reason = (
            "prerequisite_repair"
        )

    else:
        target_reason = target["reason"]

    # --------------------------------------------------
    # 4. Resolve the actual question-generation ID
    # --------------------------------------------------

    concept_id = get_concept_id(concept)

    if concept_id is None:
        raise ValueError(
            "Selected concept does not contain a valid ID. "
            f"Available keys: {list(concept.keys())}"
        )

    # --------------------------------------------------
    # 5. Generate questions for the ACTUAL target
    # --------------------------------------------------

    questions = generate_questions_for_concept(
        graph_id=graph_id,
        concept_id=concept_id,
        topic=topic,
        subject=subject,
        academic_level=academic_level,
        count=count,
        difficulty=difficulty,
        cognitive_skill=cognitive_skill,
        username=username,
    )

    # --------------------------------------------------
    # 6. Return both the learning target and the reason
    # --------------------------------------------------

    return {
        "created": True,
        "username": username,
        "recommended_action": action,
        "adaptation_reason": decision.get(
            "reason"
        ),
        "target_reason": target_reason,
    
        # Actual concept used to generate questions.
        "target_concept": concept,

        # Original concept that adaptation wanted
        # to work on, if available.
        "adaptation_target_concept": decision.get(
            "target_concept"
        ),

        # The prerequisite that caused the repair.
        "blocking_prerequisite": blocking_prerequisite,

        "questions": questions,
        "question_count": len(questions),
    }   









































