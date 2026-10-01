from typing import Any

from utils.database import get_connection
from services.knowledge_graph_service import (
    get_prerequisite_concepts,
)


PREREQUISITE_MASTERY_THRESHOLD = 0.60


def get_active_retest_targets(
    username: str,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """
    Returns the learner's active retest targets.

    Retest targets represent specific unresolved weaknesses
    that should receive focused follow-up.
    """

    if limit < 1:
        raise ValueError("limit must be at least 1")

    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                rt.id,
                rt.concept_id,
                c.graph_id,
                c.concept_key,
                c.name,
                c.description,
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
            ORDER BY
                rt.priority DESC,
                rt.created_at ASC
            LIMIT ?
            """,
            (username, limit),
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


def get_learner_snapshot(
    username: str,
) -> dict[str, Any]:
    """
    Returns the learner's current adaptive state.

    Includes:
    - concept mastery
    - weak concepts
    - strong concepts
    - skill estimates
    - active error patterns
    - active retest targets
    """

    conn = get_connection()

    try:
        concept_rows = conn.execute(
            """
            SELECT
                lcs.concept_id,
                c.graph_id,
                c.concept_key,
                c.name,
                c.description,
                lcs.mastery,
                lcs.confidence,
                lcs.evidence_count,
                lcs.recent_accuracy,
                lcs.trend,
                lcs.status,
                lcs.last_evidence_at
            FROM learner_concept_state lcs
            JOIN concepts c
                ON c.id = lcs.concept_id
            WHERE lcs.username = ?
            ORDER BY
                lcs.mastery ASC,
                lcs.evidence_count DESC
            """,
            (username,),
        ).fetchall()

        skill_rows = conn.execute(
            """
            SELECT
                skill_key,
                estimate,
                confidence,
                evidence_count,
                recent_accuracy,
                trend
            FROM learner_skill_state
            WHERE username = ?
            ORDER BY estimate ASC
            """,
            (username,),
        ).fetchall()

        error_rows = conn.execute(
            """
            SELECT
                id,
                concept_id,
                pattern_key,
                category,
                description,
                occurrences,
                confidence,
                status,
                first_seen_at,
                last_seen_at
            FROM learner_error_patterns
            WHERE username = ?
              AND status = 'active'
            ORDER BY
                occurrences DESC,
                confidence DESC
            """,
            (username,),
        ).fetchall()

        concepts = [dict(row) for row in concept_rows]
        skills = [dict(row) for row in skill_rows]
        errors = [dict(row) for row in error_rows]

        weak_concepts = [
            concept
            for concept in concepts
            if float(concept["mastery"]) < 0.6
        ]

        strong_concepts = [
            concept
            for concept in concepts
            if float(concept["mastery"]) >= 0.8
        ]

        retest_targets = get_active_retest_targets(
            username=username,
            limit=3,
        )

        return {
            "username": username,
            "all_concepts": concepts,
            "weak_concepts": weak_concepts,
            "strong_concepts": strong_concepts,
            "skills": skills,
            "active_error_patterns": errors,
            "active_retest_targets": retest_targets,
            "concept_count": len(concepts),
            "weak_concept_count": len(weak_concepts),
            "error_pattern_count": len(errors),
            "active_retest_target_count": len(
                retest_targets
            ),
        }

    finally:
        conn.close()


def _find_weak_prerequisite(
    snapshot: dict[str, Any],
    concept: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Finds the weakest direct prerequisite of a concept.

    Returns the prerequisite only when its mastery is below
    the prerequisite threshold.
    """

    graph_id = concept.get("graph_id")
    concept_id = concept.get("concept_id")

    if graph_id is None or concept_id is None:
        return None

    prerequisites = get_prerequisite_concepts(
        graph_id=graph_id,
        concept_id=concept_id,
    )

    if not prerequisites:
        return None

    concept_states = {
        state["concept_id"]: state
        for state in snapshot["all_concepts"]
    }

    weak_prerequisites = []

    for prerequisite in prerequisites:
        prerequisite_id = prerequisite["concept_id"]

        state = concept_states.get(prerequisite_id)

        if state is None:
            # No learner evidence means the prerequisite
            # has not yet been established.
            enriched = {
                **prerequisite,
                "mastery": 0.0,
                "confidence": 0.0,
                "evidence_count": 0,
                "status": "unseen",
            }
            weak_prerequisites.append(enriched)
            continue

        if (
            float(state["mastery"])
            < PREREQUISITE_MASTERY_THRESHOLD
        ):
            enriched = {
                **prerequisite,
                "mastery": state["mastery"],
                "confidence": state["confidence"],
                "evidence_count": state["evidence_count"],
                "recent_accuracy": state[
                    "recent_accuracy"
                ],
                "trend": state["trend"],
                "status": state["status"],
            }
            weak_prerequisites.append(enriched)

    if not weak_prerequisites:
        return None

    weak_prerequisites.sort(
        key=lambda item: (
            float(item.get("mastery", 0.0)),
            -float(item.get("importance", 0.0)),
        )
    )

    return weak_prerequisites[0]


def _build_prerequisite_repair_decision(
    snapshot: dict[str, Any],
    concept: dict[str, Any],
    prerequisite: dict[str, Any],
) -> dict[str, Any]:
    """
    Builds the adaptation decision when a prerequisite
    is weaker than the target concept.
    """

    return {
        "action": "prerequisite_repair",
        "reason": (
            f"The target concept '{concept['name']}' "
            f"depends on the prerequisite "
            f"'{prerequisite['name']}', which currently "
            f"has insufficient mastery."
        ),
        "priority_concepts": [prerequisite],
        "target_concept": concept,
        "blocking_prerequisite": prerequisite,
        "priority_errors": snapshot[
            "active_error_patterns"
        ][:3],
        "priority_retest_targets": snapshot[
            "active_retest_targets"
        ],
        "snapshot": snapshot,
    }


def choose_next_action(
    username: str,
) -> dict[str, Any]:
    """
    Chooses the next learning action from learner evidence.

    Possible actions:
    - start_learning
    - reteach
    - prerequisite_repair
    - targeted_practice
    - mixed_retest
    - advance

    Priority order:
    1. Active retest targets
    2. Prerequisite repair for those targets
    3. Active error patterns
    4. Prerequisite repair for error concepts
    5. Generic weak concepts
    6. Advance
    """

    snapshot = get_learner_snapshot(username)

    if snapshot["concept_count"] == 0:
        return {
            "action": "start_learning",
            "reason": "No learner evidence exists yet.",
            "priority_concepts": [],
            "priority_errors": [],
            "priority_retest_targets": [],
            "snapshot": snapshot,
        }

    weak_concepts = snapshot["weak_concepts"]
    errors = snapshot["active_error_patterns"]
    retest_targets = snapshot["active_retest_targets"]

    # --------------------------------------------------
    # 1. Active retest targets have highest priority
    # --------------------------------------------------

    if retest_targets:
        target_concept_ids = [
            target["concept_id"]
            for target in retest_targets
        ]

        priority_concepts = []

        for concept in snapshot["all_concepts"]:
            if concept["concept_id"] in target_concept_ids:
                priority_concepts.append(concept)

        # Before practicing the target, check whether
        # one of its prerequisites is weaker.
        for concept in priority_concepts:
            prerequisite = _find_weak_prerequisite(
                snapshot=snapshot,
                concept=concept,
            )

            if prerequisite is not None:
                return _build_prerequisite_repair_decision(
                    snapshot=snapshot,
                    concept=concept,
                    prerequisite=prerequisite,
                )

        return {
            "action": "targeted_practice",
            "reason": (
                "An active retest target identifies an "
                "unresolved learner weakness that needs "
                "focused practice."
            ),
            "priority_concepts": priority_concepts[:3],
            "priority_errors": errors[:3],
            "priority_retest_targets": retest_targets,
            "target_retest": retest_targets[0],
            "snapshot": snapshot,
        }

    # --------------------------------------------------
    # 2. Active error patterns
    # --------------------------------------------------

    if errors:
        highest_error = errors[0]
        error_concept_id = highest_error.get(
            "concept_id"
        )

        priority_concepts = []

        if error_concept_id is not None:
            priority_concepts = [
                concept
                for concept in snapshot["all_concepts"]
                if concept["concept_id"] == error_concept_id
            ]

        if not priority_concepts:
            priority_concepts = weak_concepts[:3]

        # Check prerequisite before targeted practice.
        for concept in priority_concepts:
            prerequisite = _find_weak_prerequisite(
                snapshot=snapshot,
                concept=concept,
            )

            if prerequisite is not None:
                return _build_prerequisite_repair_decision(
                    snapshot=snapshot,
                    concept=concept,
                    prerequisite=prerequisite,
                )

        return {
            "action": "targeted_practice",
            "reason": (
                "An active error pattern needs focused "
                "practice."
            ),
            "priority_concepts": priority_concepts[:3],
            "priority_errors": errors[:3],
            "priority_retest_targets": [],
            "target_error": highest_error,
            "snapshot": snapshot,
        }

    # --------------------------------------------------
    # 3. Generic weak concepts
    # --------------------------------------------------

    if weak_concepts:
        weakest_concept = weak_concepts[0]

        # Check prerequisite before reteaching/testing
        # the weak concept itself.
        prerequisite = _find_weak_prerequisite(
            snapshot=snapshot,
            concept=weakest_concept,
        )

        if prerequisite is not None:
            return _build_prerequisite_repair_decision(
                snapshot=snapshot,
                concept=weakest_concept,
                prerequisite=prerequisite,
            )

        if float(weakest_concept["mastery"]) < 0.35:
            action = "reteach"
            reason = (
                "A concept has very low mastery and needs "
                "re-teaching before another test."
            )
        else:
            action = "mixed_retest"
            reason = (
                "The learner needs another test to confirm "
                "improvement on weak concepts."
            )

        return {
            "action": action,
            "reason": reason,
            "priority_concepts": weak_concepts[:3],
            "priority_errors": [],
            "priority_retest_targets": [],
            "snapshot": snapshot,
        }

    # --------------------------------------------------
    # 4. No major weakness
    # --------------------------------------------------

    return {
        "action": "advance",
        "reason": (
            "No major weak concepts were detected. "
            "The learner can move toward new or harder "
            "material."
        ),
        "priority_concepts": [],
        "priority_errors": [],
        "priority_retest_targets": [],
        "snapshot": snapshot,
    }


def build_adaptation_prompt_context(
    username: str,
) -> dict[str, Any]:
    """
    Creates a compact learner context for future AI prompts.
    """

    snapshot = get_learner_snapshot(username)
    decision = choose_next_action(username)

    return {
        "username": username,
        "recommended_action": decision["action"],
        "decision_reason": decision["reason"],
        "priority_concepts": decision[
            "priority_concepts"
        ][:5],
        "priority_retest_targets": decision.get(
            "priority_retest_targets",
            [],
        )[:5],
        "blocking_prerequisite": decision.get(
            "blocking_prerequisite"
        ),
        "target_concept": decision.get(
            "target_concept"
        ),
        "weak_concepts": snapshot[
            "weak_concepts"
        ][:5],
        "active_error_patterns": snapshot[
            "active_error_patterns"
        ][:5],
        "skill_estimates": snapshot["skills"],
    }


def get_adaptation_after_quiz(
    username: str,
    session_id: int,
) -> dict[str, Any]:
    """
    Combines the completed quiz result with the learner's
    current adaptive decision.

    This is the bridge:

        Quiz session
              ↓
        Result summary
              ↓
        Learner state
              ↓
        Knowledge graph
              ↓
        Adaptation decision
    """

    from services.learner_state_service import (
        get_quiz_result_summary,
    )

    session = get_quiz_result_summary(session_id)

    if session["username"] != username:
        raise ValueError(
            "Quiz session does not belong to this learner."
        )

    decision = choose_next_action(username)

    return {
        "session_id": session_id,
        "username": username,
        "quiz_result": session,
        "next_action": decision["action"],
        "decision_reason": decision["reason"],
        "priority_concepts": decision[
            "priority_concepts"
        ],
        "priority_errors": decision[
            "priority_errors"
        ],
        "priority_retest_targets": decision[
            "priority_retest_targets"
        ],
        "target_retest": decision.get(
            "target_retest"
        ),
        "target_error": decision.get(
            "target_error"
        ),
        "target_concept": decision.get(
            "target_concept"
        ),
        "blocking_prerequisite": decision.get(
            "blocking_prerequisite"
        ),
    }