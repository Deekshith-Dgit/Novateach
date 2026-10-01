from dataclasses import dataclass, field
from typing import Any


@dataclass
class TopicResolution:
    """
    Result of resolving a student's requested learning topic.

    This model contains both:
    1. Basic topic resolution information
    2. Semantic information about what kind of content the topic needs

    The semantic information is later used by the lesson planner
    and textbook production system to control the type of content
    that should be generated.
    """

    status: str
    topic: str
    subject: str | None = None
    reason: str | None = None
    possible_subjects: list[str] = field(default_factory=list)

    # ========================================================
    # SEMANTIC TOPIC PROFILE
    # ========================================================

    domain: str | None = None

    topic_type: str | None = None

    content_modes: list[str] = field(default_factory=list)

    formula_relevant: bool | None = None

    quantitative_relevant: bool | None = None

    def is_valid(self) -> bool:
        """
        Return True when the topic was successfully resolved.
        """
        return self.status == "valid"

    def needs_clarification(self) -> bool:
        """
        Return True when more information is needed from the student.
        """
        return self.status == "ambiguous"

    def is_invalid(self) -> bool:
        """
        Return True when the topic cannot currently be resolved.
        """
        return self.status == "invalid"

    def has_semantic_profile(self) -> bool:
        """
        Return True when the topic contains enough semantic
        information for downstream lesson planning.

        We require the three most important semantic fields:
        - domain
        - topic_type
        - formula_relevant
        """
        return (
            bool(self.domain)
            and bool(self.topic_type)
            and self.formula_relevant is not None
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the topic resolution into a normal dictionary.

        This is useful when passing the resolved topic into
        prompts, logs, or other services.
        """
        return {
            "status": self.status,
            "topic": self.topic,
            "subject": self.subject,
            "reason": self.reason,
            "possible_subjects": self.possible_subjects,
            "domain": self.domain,
            "topic_type": self.topic_type,
            "content_modes": self.content_modes,
            "formula_relevant": self.formula_relevant,
            "quantitative_relevant": self.quantitative_relevant,
        }


@dataclass
class LearningSignalResult:
    """
    Result of extracting learning-related signals from user input.
    """

    relevant: bool
    learning_signals: list[str] = field(default_factory=list)