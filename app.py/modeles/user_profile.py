from typing import Any


class UserProfile:
    """
    Stores learner-provided identity, preferences, and onboarding signals.

    Important:
    This model stores what the user explicitly tells Novateach.

    It must not be treated as quiz-derived learner evidence.
    Fields such as mastery, application ability, logical reasoning,
    recurring error patterns, and concept confidence belong to the
    adaptive learner model, not this user-provided profile.
    """

    def __init__(
        self,
        name: str,
        learning_style: str = "",
        confusion_pattern: str = "",
        difficulty_trigger: str = "",
        learning_goal: str = "",
        confidence_level: str = "",
        personal_info: str = "",
        learning_snapshot: str = "",
        interest_area: str | None = None,

        # ========================================================
        # ACCOUNT IDENTITY
        # ========================================================

        username: str = "",

        # ========================================================
        # PERSONALIZATION SIGNALS
        # ========================================================

        understanding_strategy: str | None = None,
        support_strategy: str | None = None,
        retention_pattern: str | None = None,
        pace_preference: str | None = None,
        teaching_strategy: str | None = None,

        recovery_strategy: str | None = None,

        onboarding_answers: dict[str, Any] | None = None,
        profile_summary: dict[str, Any] | str | None = None,
        free_text_learning_signals: list[str] | None = None,
        saved_interests: list[dict[str, str]] | None = None,

        # ========================================================
        # LEGACY / FUTURE DATA
        #
        # Keep these optional so existing code is not broken.
        # Actual evidence should be stored in learner-model tables.
        # ========================================================

        learning_history: list[Any] | None = None,
        blindspots: list[Any] | None = None,
        feedback_history: list[Any] | None = None,
    ):
        self.username = self._clean_string(username)
        self.name = self._clean_string(name)

        # ========================================================
        # EXISTING PROFILE DATA
        # ========================================================

        self.learning_style = self._clean_string(learning_style)
        self.confusion_pattern = self._clean_string(confusion_pattern)
        self.difficulty_trigger = self._clean_string(difficulty_trigger)
        self.learning_goal = self._clean_string(learning_goal)
        self.confidence_level = self._clean_string(confidence_level)
        self.personal_info = self._clean_string(personal_info)
        self.learning_snapshot = self._clean_string(learning_snapshot)

        self.interest_area = self._clean_optional_string(
            interest_area
        )

        # ========================================================
        # NEW PERSONALIZATION DATA
        # ========================================================

        self.understanding_strategy = self._clean_optional_string(
            understanding_strategy
        )

        self.support_strategy = self._clean_optional_string(
            support_strategy
        )

        self.retention_pattern = self._clean_optional_string(
            retention_pattern
        )

        self.pace_preference = self._clean_optional_string(
            pace_preference
        )

        self.teaching_strategy = self._clean_optional_string(
            teaching_strategy
        )

        self.recovery_strategy = self._clean_optional_string(
            recovery_strategy
        )

        self.onboarding_answers = (
            dict(onboarding_answers)
            if isinstance(onboarding_answers, dict)
            else {}
        )

        self.profile_summary = profile_summary

        self.free_text_learning_signals = (
            [
                self._clean_string(signal)
                for signal in free_text_learning_signals
                if isinstance(signal, str) and signal.strip()
            ]
            if isinstance(free_text_learning_signals, list)
            else []
        )

        self.saved_interests = (
            [
                {
                    "topic": item["topic"].strip(),
                    "subject": item["subject"].strip(),
                    "status": item["status"],
                }
                for item in saved_interests
                if isinstance(item, dict)
                and isinstance(item.get("topic"), str)
                and item["topic"].strip()
                and isinstance(item.get("subject"), str)
                and item["subject"].strip()
                and item.get("status") in {"saved", "later"}
            ]
            if isinstance(saved_interests, list)
            else []
        )

        # ========================================================
        # LEGACY / FUTURE ADAPTIVE LEARNING DATA
        #
        # Do not rely on these for the v1 learner model.
        # Use learner_evidence and learner_* tables instead.
        # ========================================================

        self.learning_history = (
            list(learning_history)
            if isinstance(learning_history, list)
            else []
        )

        self.blindspots = (
            list(blindspots)
            if isinstance(blindspots, list)
            else []
        )

        self.feedback_history = (
            list(feedback_history)
            if isinstance(feedback_history, list)
            else []
        )

    # ============================================================
    # INTERNAL NORMALIZATION HELPERS
    # ============================================================

    @staticmethod
    def _clean_string(value: Any) -> str:
        if value is None:
            return ""

        if not isinstance(value, str):
            return str(value).strip()

        return value.strip()

    @classmethod
    def _clean_optional_string(
        cls,
        value: Any,
    ) -> str | None:
        cleaned = cls._clean_string(value)
        return cleaned or None

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self) -> str:
        return (
            "UserProfile("
            f"username={self.username or 'Not set'}, "
            f"name={self.name or 'Not set'}, "
            f"style={self.learning_style or 'Not specified'}, "
            f"interest={self.interest_area or 'Not specified'}"
            ")"
        )

    # ============================================================
    # BASIC SUMMARY
    # ============================================================

    def get_summary(self) -> str:
        return f"""
👤 Name: {self.name or 'Not specified'}

🎨 Learning Style: {self.learning_style or 'Not specified'}

❓ Confusion Pattern: {self.confusion_pattern or 'Not specified'}

⚡ Difficulty Trigger: {self.difficulty_trigger or 'Not specified'}

🎯 Learning Goal: {self.learning_goal or 'Not specified'}

💪 Confidence / Mindset: {self.confidence_level or 'Not specified'}

🌟 Interest Area: {self.interest_area or 'Not specified'}

🧠 Understanding Strategy:
{self.understanding_strategy or 'Not specified'}

🔧 Support Strategy:
{self.support_strategy or 'Not specified'}

🧠 Retention Pattern:
{self.retention_pattern or 'Not specified'}

⏱️ Pace Preference:
{self.pace_preference or 'Not specified'}

📚 Teaching Strategy:
{self.teaching_strategy or 'Not specified'}

🛠️ Recovery Strategy:
{self.recovery_strategy or 'Not specified'}
""".strip()

    # ============================================================
    # PERSONALIZATION SUMMARY
    # ============================================================

    def get_personalization_summary(self) -> dict[str, Any]:
        """
        Compact student-provided preference summary.

        This can be passed to lesson planning, but lesson planners
        should treat it as a preference signal—not a fixed judgment
        about the learner.
        """

        return {
            "username": self.username,
            "name": self.name,

            "understanding_strategy":
                self.understanding_strategy,

            "support_strategy":
                self.support_strategy,

            "difficulty_trigger":
                self.difficulty_trigger,

            "retention_pattern":
                self.retention_pattern,

            "pace_preference":
                self.pace_preference,

            "teaching_strategy":
                self.teaching_strategy,

            "recovery_strategy":
                self.recovery_strategy,

            "learning_goal":
                self.learning_goal,

            "interest_area":
                self.interest_area,

            "free_text_learning_signals":
                self.free_text_learning_signals,

            "saved_interests":
                self.saved_interests,
        }

    # ============================================================
    # SERIALIZATION
    # ============================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Full profile format for database/API/JSON use.
        """

        return {
            "username": self.username,
            "name": self.name,

            "learning_style": self.learning_style,
            "confusion_pattern": self.confusion_pattern,
            "difficulty_trigger": self.difficulty_trigger,
            "learning_goal": self.learning_goal,
            "confidence_level": self.confidence_level,
            "personal_info": self.personal_info,
            "learning_snapshot": self.learning_snapshot,
            "interest_area": self.interest_area,

            "understanding_strategy":
                self.understanding_strategy,

            "support_strategy":
                self.support_strategy,

            "retention_pattern":
                self.retention_pattern,

            "pace_preference":
                self.pace_preference,

            "teaching_strategy":
                self.teaching_strategy,

            "recovery_strategy":
                self.recovery_strategy,

            "onboarding_answers":
                self.onboarding_answers,

            "profile_summary":
                self.profile_summary,

            "free_text_learning_signals":
                self.free_text_learning_signals,

            "saved_interests":
                self.saved_interests,

            "learning_history":
                self.learning_history,

            "blindspots":
                self.blindspots,

            "feedback_history":
                self.feedback_history,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "UserProfile":
        """
        Restore a UserProfile from a database/API dictionary.
        """

        if not isinstance(data, dict):
            raise ValueError(
                "UserProfile.from_dict expects a dictionary."
            )

        return cls(
            username=data.get("username", ""),
            name=data.get("name", ""),

            learning_style=data.get("learning_style", ""),
            confusion_pattern=data.get(
                "confusion_pattern",
                "",
            ),
            difficulty_trigger=data.get(
                "difficulty_trigger",
                "",
            ),
            learning_goal=data.get("learning_goal", ""),
            confidence_level=data.get(
                "confidence_level",
                "",
            ),
            personal_info=data.get("personal_info", ""),
            learning_snapshot=data.get(
                "learning_snapshot",
                "",
            ),
            interest_area=data.get("interest_area"),

            understanding_strategy=data.get(
                "understanding_strategy",
            ),
            support_strategy=data.get("support_strategy"),
            retention_pattern=data.get("retention_pattern"),
            pace_preference=data.get("pace_preference"),
            teaching_strategy=data.get("teaching_strategy"),
            recovery_strategy=data.get("recovery_strategy"),

            onboarding_answers=data.get(
                "onboarding_answers",
                {},
            ),
            profile_summary=data.get("profile_summary"),
            free_text_learning_signals=data.get(
                "free_text_learning_signals",
                [],
            ),
            saved_interests=data.get(
                "saved_interests",
                [],
            ),

            learning_history=data.get("learning_history", []),
            blindspots=data.get("blindspots", []),
            feedback_history=data.get(
                "feedback_history",
                [],
            ),
        )

    # ============================================================
    # FRONTEND ONBOARDING FACTORY
    # ============================================================

    @classmethod
    def from_personalization_answers(
        cls,
        username: str,
        name: str,
        answers: dict[str, Any],
        extra_learning_info: str = "",
    ) -> "UserProfile":
        """
        Create a profile from your new React personalization flow.

        Expected React answer keys:
        - understanding_strategy
        - support_strategy
        - difficulty_trigger
        - teaching_strategy
        - retention_pattern
        - pace_preference
        """

        if not isinstance(answers, dict):
            raise ValueError(
                "Personalization answers must be a dictionary."
            )

        extra_info = cls._clean_string(extra_learning_info)

        free_text_signals = (
            [extra_info]
            if extra_info
            else []
        )

        return cls(
            username=username,
            name=name,

            understanding_strategy=answers.get(
                "understanding_strategy",
            ),
            support_strategy=answers.get(
                "support_strategy",
            ),
            difficulty_trigger=answers.get(
                "difficulty_trigger",
                "",
            ),
            teaching_strategy=answers.get(
                "teaching_strategy",
            ),
            retention_pattern=answers.get(
                "retention_pattern",
            ),
            pace_preference=answers.get(
                "pace_preference",
            ),

            onboarding_answers=answers,
            free_text_learning_signals=free_text_signals,

            # These are unknown at onboarding.
            learning_style="",
            confusion_pattern="",
            learning_goal="",
            confidence_level="",
            personal_info="",
            learning_snapshot="",
            interest_area=None,
        )

    # ============================================================
    # COMPLETENESS CHECK
    # ============================================================

    def has_completed_personalization(self) -> bool:
        """
        Check if all six required React personalization answers exist.
        """

        required_values = [
            self.understanding_strategy,
            self.support_strategy,
            self.difficulty_trigger,
            self.teaching_strategy,
            self.retention_pattern,
            self.pace_preference,
        ]

        return all(
            isinstance(value, str) and value.strip()
            for value in required_values
        )

    # ============================================================
    # PROFILE DISPLAY
    # ============================================================

    def display_profile(self) -> None:
        print("\n" + "=" * 70)
        print(
            f"📋 {self.name or 'Student'}'s "
            "Personalized Learning Profile"
        )
        print("=" * 70)
        print(self.get_summary())
        print("\n" + "=" * 70)