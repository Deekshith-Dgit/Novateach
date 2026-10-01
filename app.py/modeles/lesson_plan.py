from dataclasses import dataclass, field
from typing import Any


# ============================================================
# LESSON REQUEST
# ============================================================

@dataclass
class LessonRequest:
    """
    Represents the complete request for a lesson.

    topic_profile carries the semantic analysis performed by
    the Topic Resolver.

    Example:
    {
        "domain": "behavioural_science",
        "topic_type": "social_behavioural",
        "content_modes": [
            "concepts",
            "definitions",
            "theories",
            "mechanisms",
            "examples",
            "scenarios"
        ],
        "formula_relevant": False,
        "quantitative_relevant": False
    }
    """

    topic: str
    subject: str
    academic_level: str
    difficulty: str

    # Semantic topic information from Topic Resolver.
    topic_profile: dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# LEARNING BLUEPRINT
# ============================================================

@dataclass
class LearningBlueprint:
    """
    Represents the pedagogical blueprint created by the
    Lesson Planner.

    topic_profile is carried forward from the Topic Resolver
    so downstream systems, especially Lecture Production,
    know what kind of content naturally belongs to the topic.
    """

    topic: str
    subject: str
    academic_level: str
    difficulty: str

    learning_objectives: list[str] = field(
        default_factory=list
    )

    prerequisites: list[str] = field(
        default_factory=list
    )

    concepts: list[dict] = field(
        default_factory=list
    )

    concept_sequence: list[str] = field(
        default_factory=list
    )

    teaching_strategy: dict = field(
        default_factory=dict
    )

    # ========================================================
    # SEMANTIC TOPIC PROFILE
    # ========================================================

    topic_profile: dict[str, Any] = field(
        default_factory=dict
    )

    # ========================================================
    # CONVERT TO DICTIONARY
    # ========================================================

    def to_dict(self):
        """
        Convert the LearningBlueprint into a dictionary.

        The topic_profile is intentionally included because
        downstream systems need the semantic constraints.
        """

        return {
            "topic": self.topic,
            "subject": self.subject,
            "academic_level": self.academic_level,
            "difficulty": self.difficulty,
            "learning_objectives": self.learning_objectives,
            "prerequisites": self.prerequisites,
            "concepts": self.concepts,
            "concept_sequence": self.concept_sequence,
            "teaching_strategy": self.teaching_strategy,
            "topic_profile": self.topic_profile,
        }

    # ========================================================
    # CREATE FROM AI DICTIONARY
    # ========================================================

    @classmethod
    def from_dict(cls, data):

        if not isinstance(data, dict):
            raise ValueError(
                "LearningBlueprint data must be a dictionary."
            )

        required_fields = [
            "topic",
            "subject",
            "academic_level",
            "difficulty",
            "learning_objectives",
            "prerequisites",
            "concepts",
            "concept_sequence",
            "teaching_strategy",
        ]

        # ----------------------------------------------------
        # REQUIRED FIELD CHECK
        # ----------------------------------------------------

        missing = [
            field_name
            for field_name in required_fields
            if field_name not in data
        ]

        if missing:
            raise ValueError(
                f"LearningBlueprint missing fields: {missing}"
            )

        # ----------------------------------------------------
        # STRING FIELD VALIDATION
        # ----------------------------------------------------

        string_fields = [
            "topic",
            "subject",
            "academic_level",
            "difficulty",
        ]

        for field_name in string_fields:
            if not isinstance(
                data[field_name],
                str
            ):
                raise ValueError(
                    f"LearningBlueprint '{field_name}' "
                    f"must be a string."
                )

        # ----------------------------------------------------
        # LIST FIELD VALIDATION
        # ----------------------------------------------------

        if not isinstance(
            data["learning_objectives"],
            list
        ):
            raise ValueError(
                "LearningBlueprint 'learning_objectives' "
                "must be a list."
            )

        if not isinstance(
            data["prerequisites"],
            list
        ):
            raise ValueError(
                "LearningBlueprint 'prerequisites' "
                "must be a list."
            )

        if not isinstance(
            data["concepts"],
            list
        ):
            raise ValueError(
                "LearningBlueprint 'concepts' "
                "must be a list."
            )

        if not isinstance(
            data["concept_sequence"],
            list
        ):
            raise ValueError(
                "LearningBlueprint 'concept_sequence' "
                "must be a list."
            )

        # ----------------------------------------------------
        # LIST ITEM VALIDATION
        # ----------------------------------------------------

        if not all(
            isinstance(item, str)
            for item in data["learning_objectives"]
        ):
            raise ValueError(
                "Every learning objective must be a string."
            )

        if not all(
            isinstance(item, str)
            for item in data["prerequisites"]
        ):
            raise ValueError(
                "Every prerequisite must be a string."
            )

        if not all(
            isinstance(item, dict)
            for item in data["concepts"]
        ):
            raise ValueError(
                "Every concept must be a dictionary."
            )

        if not all(
            isinstance(item, str)
            for item in data["concept_sequence"]
        ):
            raise ValueError(
                "Every concept sequence item "
                "must be a string."
            )

        # ----------------------------------------------------
        # TEACHING STRATEGY VALIDATION
        # ----------------------------------------------------

        if not isinstance(
            data["teaching_strategy"],
            dict
        ):
            raise ValueError(
                "LearningBlueprint 'teaching_strategy' "
                "must be a dictionary."
            )

        # ----------------------------------------------------
        # TOPIC PROFILE VALIDATION
        # ----------------------------------------------------

        topic_profile = data.get(
            "topic_profile",
            {}
        )

        if not isinstance(topic_profile, dict):
            raise ValueError(
                "LearningBlueprint 'topic_profile' "
                "must be a dictionary."
            )

        # ----------------------------------------------------
        # CREATE BLUEPRINT
        # ----------------------------------------------------

        return cls(
            topic=data["topic"],
            subject=data["subject"],
            academic_level=data["academic_level"],
            difficulty=data["difficulty"],
            learning_objectives=data["learning_objectives"],
            prerequisites=data["prerequisites"],
            concepts=data["concepts"],
            concept_sequence=data["concept_sequence"],
            teaching_strategy=data["teaching_strategy"],
            topic_profile=topic_profile,
        )