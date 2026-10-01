import json
from pathlib import Path
from typing import Any

from ai_generator import generate_with_ai
from modeles.user_profile import UserProfile
from planners.input_resolver import extract_learning_signals

APP_DIR = Path(__file__).resolve().parent.parent
from utils.database import (
    load_personalization_profile,
    load_user,
    mark_onboarding_complete,
    save_personalization_profile,
    save_user,
    update_user_profile,
    user_exists,
)


# ============================================================
# PERSONALIZATION QUESTION KEYS
# ============================================================

REQUIRED_PERSONALIZATION_KEYS = {
    "understanding_strategy",
    "support_strategy",
    "difficulty_trigger",
    "teaching_strategy",
    "retention_pattern",
    "pace_preference",
}


# ============================================================
# ASK USER TO CHOOSE AN OPTION
#
# Legacy CLI helper. Keep it because your old command-line
# onboarding can still work while you build the web frontend.
# ============================================================

def ask_choice(
    question: str,
    options: dict[str, str],
) -> str:
    while True:
        print(f"\n{question}")

        for key, text in options.items():
            print(f"{key}. {text}")

        answer = input("Choose: ").strip().upper()

        if answer in options:
            return options[answer]

        print(
            "Invalid input. Please choose one of the given options."
        )


# ============================================================
# VALIDATION
# ============================================================

def validate_personalization_answers(
    answers: dict[str, Any],
) -> list[str]:
    """
    Return a list of missing/invalid required personalization keys.

    The frontend and CLI must both collect these six fields.
    """

    if not isinstance(answers, dict):
        return sorted(REQUIRED_PERSONALIZATION_KEYS)

    return sorted(
        key
        for key in REQUIRED_PERSONALIZATION_KEYS
        if not isinstance(answers.get(key), str)
        or not answers[key].strip()
    )


# ============================================================
# GENERATE PROFILE SUMMARY
# ============================================================

def generate_profile_summary(
    answers: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate a teaching-preference summary.

    This must not claim mastery or permanent learner traits.
    """

    prompt_path = (
        APP_DIR
        / "prompts"
        / "profile_prompt.txt"
    )

    if not prompt_path.exists():
        raise FileNotFoundError(
            "Profile prompt not found: "
            f"{prompt_path}"
        )

    prompt_template = prompt_path.read_text(
        encoding="utf-8",
    )

    prompt = prompt_template.replace(
        "{answers}",
        json.dumps(
            answers,
            indent=2,
            ensure_ascii=False,
        ),
    )

    profile_summary = generate_with_ai(
        prompt,
        expect_json=True,
    )

    if not isinstance(profile_summary, dict):
        raise ValueError(
            "AI returned an invalid profile summary.",
        )

    return profile_summary

# ============================================================
# FREE-TEXT SIGNAL EXTRACTION
# ============================================================

def extract_free_text_learning_signals(
    extra_learning_info: str,
) -> list[str]:
    """
    Extract optional signals from the student's free-text answer.

    If no free text exists, do not call the AI/signal extractor.
    """

    extra_learning_info = (
        extra_learning_info.strip()
        if isinstance(extra_learning_info, str)
        else ""
    )

    if not extra_learning_info:
        return []

    result = extract_learning_signals(
        extra_learning_info
    )

    learning_signals = getattr(
        result,
        "learning_signals",
        [],
    )

    if not isinstance(learning_signals, list):
        return []

    return [
        signal.strip()
        for signal in learning_signals
        if isinstance(signal, str) and signal.strip()
    ]


# ============================================================
# CREATE PROFILE OBJECT
# ============================================================

def build_user_profile(
    username: str,
    name: str,
    answers: dict[str, Any],
    extra_learning_info: str = "",
    profile_summary: dict[str, Any] | None = None,
    free_text_learning_signals: list[str] | None = None,
) -> UserProfile:
    """
    Convert raw onboarding answers into your existing UserProfile.

    This is the one shared profile-construction path for:
    - CLI onboarding
    - React onboarding endpoint
    - future profile edit page
    """

    missing_keys = validate_personalization_answers(
        answers
    )

    if missing_keys:
        raise ValueError(
            "Missing required personalization answers: "
            + ", ".join(missing_keys)
        )

    extra_learning_info = (
        extra_learning_info.strip()
        if isinstance(extra_learning_info, str)
        else ""
    )

    if free_text_learning_signals is None:
        free_text_learning_signals = (
            extract_free_text_learning_signals(
                extra_learning_info
            )
        )

    onboarding_answers = {
        "username": username,
        "name": name,
        "understanding_strategy": answers[
            "understanding_strategy"
        ],
        "support_strategy": answers[
            "support_strategy"
        ],
        "difficulty_trigger": answers[
            "difficulty_trigger"
        ],
        "teaching_strategy": answers[
            "teaching_strategy"
        ],
        "retention_pattern": answers[
            "retention_pattern"
        ],
        "pace_preference": answers[
            "pace_preference"
        ],
        "extra_learning_info": extra_learning_info,
        "free_text_learning_signals":
            free_text_learning_signals,
    }

    return UserProfile(
        username=username,
        name=name,

        # Existing fields retained for compatibility.
        learning_style=answers[
            "understanding_strategy"
        ],
        confusion_pattern=answers[
            "support_strategy"
        ],
        difficulty_trigger=answers[
            "difficulty_trigger"
        ],
        learning_goal="Personalized learning",
        confidence_level="",
        personal_info=extra_learning_info,
        learning_snapshot="",
        interest_area=None,

        # New explicit personalization fields.
        understanding_strategy=answers[
            "understanding_strategy"
        ],
        support_strategy=answers[
            "support_strategy"
        ],
        retention_pattern=answers[
            "retention_pattern"
        ],
        pace_preference=answers[
            "pace_preference"
        ],
        teaching_strategy=answers[
            "teaching_strategy"
        ],

        onboarding_answers=onboarding_answers,
        profile_summary=profile_summary,
        free_text_learning_signals=
            free_text_learning_signals,
    )


# ============================================================
# CONVERT PROFILE TO JSON-SAFE DICTIONARY
# ============================================================

def profile_to_storage_data(
    profile: UserProfile,
) -> dict[str, Any]:
    """
    Convert UserProfile to a JSON-safe structure.

    Supports both:
    - your existing UserProfile class
    - the upgraded UserProfile class with to_dict()
    """

    if hasattr(profile, "to_dict"):
        profile_data = profile.to_dict()

        if isinstance(profile_data, dict):
            return profile_data

    return {
        "username": getattr(profile, "username", ""),
        "name": getattr(profile, "name", ""),

        "learning_style": getattr(
            profile,
            "learning_style",
            "",
        ),
        "confusion_pattern": getattr(
            profile,
            "confusion_pattern",
            "",
        ),
        "difficulty_trigger": getattr(
            profile,
            "difficulty_trigger",
            "",
        ),
        "learning_goal": getattr(
            profile,
            "learning_goal",
            "",
        ),
        "confidence_level": getattr(
            profile,
            "confidence_level",
            "",
        ),
        "personal_info": getattr(
            profile,
            "personal_info",
            "",
        ),
        "learning_snapshot": getattr(
            profile,
            "learning_snapshot",
            "",
        ),
        "interest_area": getattr(
            profile,
            "interest_area",
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
        "recovery_strategy": getattr(
            profile,
            "recovery_strategy",
            None,
        ),

        "onboarding_answers": getattr(
            profile,
            "onboarding_answers",
            {},
        ),
        "profile_summary": getattr(
            profile,
            "profile_summary",
            None,
        ),
        "free_text_learning_signals": getattr(
            profile,
            "free_text_learning_signals",
            [],
        ),
    }


# ============================================================
# SAVE PROFILE IN BOTH STORAGE FORMATS
# ============================================================

def save_profile(
    username: str,
    name: str,
    profile: UserProfile,
) -> None:
    """
    Persist the profile safely.

    Writes:
    1. users.full_profile:
       Legacy compatibility for existing CLI code/load_profile()

    2. user_personalization_profiles:
       Clean user-provided onboarding answers for the web app

    3. users.onboarding_complete:
       Allows returning users to skip onboarding
    """

    profile_data = profile_to_storage_data(profile)

    profile_json = json.dumps(
        profile_data,
        ensure_ascii=False,
    )

    if user_exists(username):
        update_user_profile(
            username=username,
            name=name,
            full_profile=profile_json,
        )
    else:
        # This path supports old CLI usage.
        # New web users must be created through auth_service.
        save_user(
            username=username,
            name=name,
            full_profile=profile_json,
        )

    answers = profile_data.get(
        "onboarding_answers",
        {},
    )

    extra_learning_info = profile_data.get(
        "personal_info",
        "",
    )

    if isinstance(answers, dict) and answers:
        save_personalization_profile(
            username=username,
            answers=answers,
            extra_learning_info=extra_learning_info,
        )

    mark_onboarding_complete(username)


# ============================================================
# WEB PERSONALIZATION SERVICE
#
# This is the function your FastAPI endpoint should call.
# ============================================================

def save_web_personalization_profile(
    username: str,
    answers: dict[str, Any],
    extra_learning_info: str = "",
) -> dict[str, Any]:
    """
    Save personalization answers sent by React.

    Frontend sends:
    {
      "username": "...",
      "answers": {
        "understanding_strategy": "...",
        "support_strategy": "...",
        "difficulty_trigger": "...",
        "teaching_strategy": "...",
        "retention_pattern": "...",
        "pace_preference": "..."
      },
      "extra_learning_info": "..."
    }
    """

    username = username.strip()

    if not username:
        return {
            "status": "error",
            "message": "Username cannot be empty.",
        }

    user = load_user(username)

    if user is None:
        return {
            "status": "error",
            "message": "User account was not found.",
        }

    missing_keys = validate_personalization_answers(
        answers
    )

    if missing_keys:
        return {
            "status": "error",
            "message": (
                "Please answer every personalization question."
            ),
            "missing_keys": missing_keys,
        }

    try:
        learning_signals = (
            extract_free_text_learning_signals(
                extra_learning_info
            )
        )

        answers_for_summary = {
            "username": username,
            "name": user["name"],
            **answers,
            "extra_learning_info": extra_learning_info,
            "free_text_learning_signals":
                learning_signals,
        }

        # AI summary improves the teaching plan,
        # but profile saving should still work if it fails.
        try:
            profile_summary = generate_profile_summary(
                answers_for_summary
            )
        except Exception as error:
            print(
                "Warning: Could not generate AI profile "
                f"summary: {error}"
            )

            profile_summary = {
                "status": "pending",
                "note": (
                    "Profile saved. AI summary can be "
                    "generated later."
                ),
            }

        profile = build_user_profile(
            username=username,
            name=user["name"],
            answers=answers,
            extra_learning_info=extra_learning_info,
            profile_summary=profile_summary,
            free_text_learning_signals=learning_signals,
        )

        save_profile(
            username=username,
            name=user["name"],
            profile=profile,
        )

        return {
            "status": "success",
            "message": (
                "Your learning preferences were saved."
            ),
            "username": username,
            "onboarding_complete": True,
            "profile_summary":
                profile.get_personalization_summary(),
        }

    except Exception as error:
        print(
            "Error while saving web personalization: "
            f"{error}"
        )

        return {
            "status": "error",
            "message": (
                "Could not save personalization settings."
            ),
        }


# ============================================================
# RUN CLI ONBOARDING
#
# This still works with your older terminal-based flow.
# ============================================================

def run_onboarding(
    username: str,
    name: str,
) -> UserProfile:
    print("\n" + "=" * 60)
    print("       NOVATEACH PERSONALIZED LEARNING SETUP")
    print("=" * 60)

    print(f"\nWelcome, {name}!")

    print(
        "Answer these questions so Novateach can adapt "
        "how it teaches you."
    )

    understanding_strategy = ask_choice(
        "1. What helps you understand a new concept fastest?",
        {
            "A": "A simple explanation",
            "B": "Examples or analogies",
            "C": "Visuals or diagrams",
            "D": "Trying problems myself",
        },
    )

    support_strategy = ask_choice(
        "2. When you are confused, what helps you most?",
        {
            "A": "Explain it more simply",
            "B": "Give me an example",
            "C": "Break it into smaller steps",
            "D": "Find exactly where I got confused",
        },
    )

    difficulty_trigger = ask_choice(
        "3. What usually makes a topic difficult for you?",
        {
            "A": "Too much information at once",
            "B": "Missing the basic concepts",
            "C": (
                "I understand theory but struggle to apply it"
            ),
            "D": "I forget what I learned",
        },
    )

    teaching_strategy = ask_choice(
        "4. How would you prefer a new topic to be taught?",
        {
            "A": "Concept → Example → Practice",
            "B": "Example → Explanation → Practice",
            "C": "Visual → Explanation → Practice",
            "D": "Problem → Concept → Practice",
        },
    )

    retention_pattern = ask_choice(
        "5. What usually happens when you revisit something later?",
        {
            "A": (
                "I remember the main idea but forget details"
            ),
            "B": "I remember it better after practicing",
            "C": "I need revision to remember it",
            "D": "I usually remember it well",
        },
    )

    pace_preference = ask_choice(
        "6. What learning pace works best for you?",
        {
            "A": "Slow and detailed",
            "B": "Moderate",
            "C": "Fast",
            "D": (
                "Adaptive — slow down when I struggle"
            ),
        },
    )

    print(
        "\n7. Is there anything else you want Novateach "
        "to know about how you learn?"
    )

    extra_learning_info = input(
        "Your answer (optional): "
    ).strip()

    answers = {
        "understanding_strategy":
            understanding_strategy,
        "support_strategy":
            support_strategy,
        "difficulty_trigger":
            difficulty_trigger,
        "teaching_strategy":
            teaching_strategy,
        "retention_pattern":
            retention_pattern,
        "pace_preference":
            pace_preference,
    }

    learning_signals = extract_free_text_learning_signals(
        extra_learning_info
    )

    answers_for_summary = {
        "username": username,
        "name": name,
        **answers,
        "extra_learning_info": extra_learning_info,
        "free_text_learning_signals": learning_signals,
    }

    print(
        "\n🧠 Building your personalized learning profile..."
    )

    try:
        profile_summary = generate_profile_summary(
            answers_for_summary
        )
    except Exception as error:
        print(
            "Warning: AI profile summary could not be "
            f"generated: {error}"
        )

        profile_summary = {
            "status": "pending",
            "note": (
                "Profile saved without AI summary."
            ),
        }

    profile = build_user_profile(
        username=username,
        name=name,
        answers=answers,
        extra_learning_info=extra_learning_info,
        profile_summary=profile_summary,
        free_text_learning_signals=learning_signals,
    )

    save_profile(
        username=username,
        name=name,
        profile=profile,
    )

    print(
        "\n✅ Profile created and saved successfully."
    )

    return profile


# ============================================================
# LOAD PROFILE
# ============================================================

def load_profile(
    username: str,
) -> UserProfile | None:
    """
    Load a full UserProfile.

    First tries users.full_profile for legacy compatibility.
    If it is empty, rebuilds a basic profile from the new
    user_personalization_profiles table.
    """

    user = load_user(username)

    if user is None:
        return None

    full_profile = user["full_profile"]

    # ========================================================
    # PREFERRED COMPATIBILITY PATH:
    # Existing full_profile JSON
    # ========================================================

    if isinstance(full_profile, str) and full_profile.strip():
        try:
            profile_data = json.loads(full_profile)

            if not isinstance(profile_data, dict):
                raise ValueError(
                    "Saved full_profile is not a dictionary."
                )

            profile_data.setdefault(
                "username",
                user["username"],
            )

            profile_data.setdefault(
                "name",
                user["name"],
            )

            if hasattr(UserProfile, "from_dict"):
                return UserProfile.from_dict(profile_data)

            return UserProfile(
                username=profile_data.get(
                    "username",
                    user["username"],
                ),
                name=profile_data.get(
                    "name",
                    user["name"],
                ),
                learning_style=profile_data.get(
                    "learning_style",
                    "",
                ),
                confusion_pattern=profile_data.get(
                    "confusion_pattern",
                    "",
                ),
                difficulty_trigger=profile_data.get(
                    "difficulty_trigger",
                    "",
                ),
                learning_goal=profile_data.get(
                    "learning_goal",
                    "",
                ),
                confidence_level=profile_data.get(
                    "confidence_level",
                    "",
                ),
                personal_info=profile_data.get(
                    "personal_info",
                    "",
                ),
                learning_snapshot=profile_data.get(
                    "learning_snapshot",
                    "",
                ),
                interest_area=profile_data.get(
                    "interest_area",
                    "",
                ),
                understanding_strategy=profile_data.get(
                    "understanding_strategy",
                ),
                support_strategy=profile_data.get(
                    "support_strategy",
                ),
                retention_pattern=profile_data.get(
                    "retention_pattern",
                ),
                pace_preference=profile_data.get(
                    "pace_preference",
                ),
                teaching_strategy=profile_data.get(
                    "teaching_strategy",
                ),
                recovery_strategy=profile_data.get(
                    "recovery_strategy",
                ),
                onboarding_answers=profile_data.get(
                    "onboarding_answers",
                    {},
                ),
                profile_summary=profile_data.get(
                    "profile_summary",
                ),
                free_text_learning_signals=profile_data.get(
                    "free_text_learning_signals",
                    [],
                ),
            )

        except (
            json.JSONDecodeError,
            ValueError,
            TypeError,
        ) as error:
            print(
                "Warning: Saved profile data is invalid: "
                f"{error}"
            )

    # ========================================================
    # FALLBACK PATH:
    # Rebuild from new user_personalization_profiles table
    # ========================================================

    personalization = load_personalization_profile(
        username
    )

    if personalization is None:
        return None

    answers = personalization.get("answers", {})

    if validate_personalization_answers(answers):
        return None

    return build_user_profile(
        username=user["username"],
        name=user["name"],
        answers=answers,
        extra_learning_info=personalization.get(
            "extra_learning_info",
            "",
        ),
        profile_summary={
            "status": "loaded_from_personalization_table"
        },
    )