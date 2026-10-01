from typing import Any

from services.profile_service import load_profile
from services.adaptation_service import (
    get_learner_snapshot,
    choose_next_action,
)


def build_learner_context(
    username: str,
) -> dict[str, Any]:
    """
    Combines profile information and learning evidence
    into one context object for AI prompts.
    """

    profile = load_profile(username)

    if profile is None:
        raise ValueError(
            f"No profile found for username: {username}"
        )

    snapshot = get_learner_snapshot(username)
    decision = choose_next_action(username)

    profile_summary = getattr(
        profile,
        "profile_summary",
        None,
    )

    if profile_summary is None:
        profile_summary = {}

    context = {
        "username": username,

        "learner_profile": {
            "name": getattr(profile, "name", None),
            "learning_style": getattr(
                profile,
                "learning_style",
                None,
            ),
            "confusion_pattern": getattr(
                profile,
                "confusion_pattern",
                None,
            ),
            "difficulty_trigger": getattr(
                profile,
                "difficulty_trigger",
                None,
            ),
            "learning_goal": getattr(
                profile,
                "learning_goal",
                None,
            ),
            "confidence_level": getattr(
                profile,
                "confidence_level",
                None,
            ),
            "understanding_strategy": getattr(
                profile,
                "understanding_strategy",
                None,
            ),
            "support_strategy": getattr(
                profile,
                "support_strategy",
                None,
            ),
            "retention_pattern": getattr(
                profile,
                "retention_pattern",
                None,
            ),
            "pace_preference": getattr(
                profile,
                "pace_preference",
                None,
            ),
            "teaching_strategy": getattr(
                profile,
                "teaching_strategy",
                None,
            ),
            "profile_summary": profile_summary,
        },

        "learning_evidence": {
            "weak_concepts": snapshot[
                "weak_concepts"
            ][:5],

            "strong_concepts": snapshot[
                "strong_concepts"
            ][:5],

            "skill_estimates": snapshot[
                "skills"
            ],

            "active_error_patterns": snapshot[
                "active_error_patterns"
            ][:5],

            "concept_count": snapshot[
                "concept_count"
            ],

            "weak_concept_count": snapshot[
                "weak_concept_count"
            ],

            "error_pattern_count": snapshot[
                "error_pattern_count"
            ],
        },

        "adaptation": {
            "recommended_action": decision[
                "action"
            ],

            "reason": decision[
                "reason"
            ],

            "priority_concepts": decision[
                "priority_concepts"
            ][:5],

            "priority_errors": decision[
                "priority_errors"
            ][:5],
        },
    }

    return context


def get_compact_learner_context(
    username: str,
) -> dict[str, Any]:
    """
    Returns only the most useful information for
    question-generation and lesson-planning prompts.
    """

    context = build_learner_context(username)

    return {
        "learner_profile": context[
            "learner_profile"
        ],

        "weak_concepts": context[
            "learning_evidence"
        ]["weak_concepts"],

        "active_error_patterns": context[
            "learning_evidence"
        ]["active_error_patterns"],

        "skill_estimates": context[
            "learning_evidence"
        ]["skill_estimates"],

        "recommended_action": context[
            "adaptation"
        ]["recommended_action"],

        "adaptation_reason": context[
            "adaptation"
        ]["reason"],
    }