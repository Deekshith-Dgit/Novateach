from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ConceptState:
    """
    Learner's current state for one concept.
    """

    concept_id: int
    username: str

    mastery: float = 0.0
    confidence: float = 0.0
    evidence_count: int = 0
    recent_accuracy: float = 0.0
    trend: str = "unknown"
    status: str = "unseen"
    last_evidence_at: Optional[str] = None

    def __post_init__(self):
        self.mastery = self._clamp(self.mastery)
        self.confidence = self._clamp(self.confidence)
        self.recent_accuracy = self._clamp(self.recent_accuracy)

    @staticmethod
    def _clamp(value: float) -> float:
        """
        Keeps a number between 0 and 1.
        """
        return max(0.0, min(1.0, float(value)))

    def update_from_evidence(
        self,
        correct: bool,
        evidence_weight: float = 0.15,
    ) -> None:
        """
        Updates mastery after one quiz evidence item.

        correct=True:
            mastery increases

        correct=False:
            mastery decreases slightly
        """

        evidence_weight = self._clamp(evidence_weight)

        old_mastery = self.mastery
        observed_result = 1.0 if correct else 0.0

        self.mastery = (
            old_mastery * (1 - evidence_weight)
            + observed_result * evidence_weight
        )

        self.evidence_count += 1
        self.recent_accuracy = observed_result
        self.confidence = min(1.0, self.confidence + 0.05)

        if self.mastery >= 0.80:
            self.status = "mastered"
        elif self.mastery >= 0.50:
            self.status = "developing"
        else:
            self.status = "needs_support"

        if self.mastery > old_mastery:
            self.trend = "improving"
        elif self.mastery < old_mastery:
            self.trend = "declining"
        else:
            self.trend = "stable"


@dataclass
class SkillState:
    """
    Learner's ability estimate for a skill.

    Examples:
    - memory
    - conceptual_understanding
    - logical_thinking
    - application
    - pattern_recognition
    """

    username: str
    skill_key: str

    estimate: float = 0.0
    confidence: float = 0.0
    evidence_count: int = 0
    recent_accuracy: float = 0.0
    trend: str = "unknown"

    def __post_init__(self):
        self.estimate = self._clamp(self.estimate)
        self.confidence = self._clamp(self.confidence)
        self.recent_accuracy = self._clamp(self.recent_accuracy)

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def update_from_evidence(
        self,
        correct: bool,
        evidence_weight: float = 0.20,
    ) -> None:
        evidence_weight = self._clamp(evidence_weight)

        old_estimate = self.estimate
        observed_result = 1.0 if correct else 0.0

        self.estimate = (
            old_estimate * (1 - evidence_weight)
            + observed_result * evidence_weight
        )

        self.evidence_count += 1
        self.recent_accuracy = observed_result
        self.confidence = min(1.0, self.confidence + 0.05)

        if self.estimate > old_estimate:
            self.trend = "improving"
        elif self.estimate < old_estimate:
            self.trend = "declining"
        else:
            self.trend = "stable"


@dataclass
class ErrorPattern:
    """
    Repeated learner mistake or misconception.
    """

    username: str
    pattern_key: str
    category: str
    description: str

    concept_id: Optional[int] = None
    occurrences: int = 1
    confidence: float = 0.5
    status: str = "active"

    def __post_init__(self):
        self.occurrences = max(1, int(self.occurrences))
        self.confidence = max(0.0, min(1.0, float(self.confidence)))

    def record_occurrence(self) -> None:
        self.occurrences += 1
        self.confidence = min(1.0, self.confidence + 0.05)


@dataclass
class LearnerState:
    """
    Complete working memory of a learner.

    This object combines:
    - concept mastery
    - skill estimates
    - recurring error patterns
    - recent learning evidence
    """

    username: str

    concept_states: dict[int, ConceptState] = field(default_factory=dict)
    skill_states: dict[str, SkillState] = field(default_factory=dict)
    error_patterns: dict[str, ErrorPattern] = field(default_factory=dict)

    recent_evidence: list[dict[str, Any]] = field(default_factory=list)

    def get_or_create_concept_state(
        self,
        concept_id: int,
    ) -> ConceptState:
        if concept_id not in self.concept_states:
            self.concept_states[concept_id] = ConceptState(
                concept_id=concept_id,
                username=self.username,
            )

        return self.concept_states[concept_id]

    def get_or_create_skill_state(
        self,
        skill_key: str,
    ) -> SkillState:
        if skill_key not in self.skill_states:
            self.skill_states[skill_key] = SkillState(
                username=self.username,
                skill_key=skill_key,
            )

        return self.skill_states[skill_key]

    def record_evidence(
        self,
        concept_id: int,
        skill_key: str,
        correct: bool,
        evidence_data: Optional[dict[str, Any]] = None,
    ) -> None:
        concept_state = self.get_or_create_concept_state(concept_id)
        skill_state = self.get_or_create_skill_state(skill_key)

        concept_state.update_from_evidence(correct=correct)
        skill_state.update_from_evidence(correct=correct)

        evidence_record = {
            "concept_id": concept_id,
            "skill_key": skill_key,
            "correct": correct,
        }

        if evidence_data:
            evidence_record.update(evidence_data)

        self.recent_evidence.append(evidence_record)

        # Keep only the latest 50 evidence records in memory.
        self.recent_evidence = self.recent_evidence[-50:]

    def add_error_pattern(
        self,
        pattern_key: str,
        category: str,
        description: str,
        concept_id: Optional[int] = None,
    ) -> ErrorPattern:
        if pattern_key in self.error_patterns:
            pattern = self.error_patterns[pattern_key]
            pattern.record_occurrence()
            return pattern

        pattern = ErrorPattern(
            username=self.username,
            pattern_key=pattern_key,
            category=category,
            description=description,
            concept_id=concept_id,
        )

        self.error_patterns[pattern_key] = pattern
        return pattern

    def get_weak_concepts(
        self,
        threshold: float = 0.50,
    ) -> list[ConceptState]:
        return [
            state
            for state in self.concept_states.values()
            if state.mastery < threshold
        ]

    def get_priority_error_patterns(self) -> list[ErrorPattern]:
        return sorted(
            self.error_patterns.values(),
            key=lambda pattern: (
                -pattern.occurrences,
                -pattern.confidence,
            ),
        )