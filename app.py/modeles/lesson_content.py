from dataclasses import dataclass, field
from typing import Any


# ============================================================
# WORKED EXAMPLE
# ============================================================

@dataclass
class WorkedExample:
    question: str
    thinking_steps: list[str] = field(default_factory=list)
    solution: str = ""
    takeaway: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "thinking_steps": self.thinking_steps,
            "solution": self.solution,
            "takeaway": self.takeaway,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkedExample":
        if not isinstance(data, dict):
            raise ValueError("WorkedExample must be a dictionary.")

        question = data.get("question")
        thinking_steps = data.get("thinking_steps", [])
        solution = data.get("solution", "")
        takeaway = data.get("takeaway", "")

        if not isinstance(question, str) or not question.strip():
            raise ValueError(
                "WorkedExample question must be a non-empty string."
            )

        if not isinstance(thinking_steps, list):
            raise ValueError(
                "WorkedExample thinking_steps must be a list."
            )

        if not all(isinstance(step, str) for step in thinking_steps):
            raise ValueError(
                "Every thinking step must be a string."
            )

        if not isinstance(solution, str):
            raise ValueError(
                "WorkedExample solution must be a string."
            )

        if not isinstance(takeaway, str):
            raise ValueError(
                "WorkedExample takeaway must be a string."
            )

        return cls(
            question=question,
            thinking_steps=thinking_steps,
            solution=solution,
            takeaway=takeaway,
        )


# ============================================================
# RETRIEVAL CHECKPOINT
# ============================================================

@dataclass
class RetrievalCheckpoint:
    question: str
    expected_idea: str
    concept_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "expected_idea": self.expected_idea,
            "concept_id": self.concept_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RetrievalCheckpoint":
        if not isinstance(data, dict):
            raise ValueError(
                "RetrievalCheckpoint must be a dictionary."
            )

        question = data.get("question")
        expected_idea = data.get("expected_idea")
        concept_id = data.get("concept_id", "")

        if not isinstance(question, str) or not question.strip():
            raise ValueError(
                "Checkpoint question must be a non-empty string."
            )

        if not isinstance(expected_idea, str):
            raise ValueError(
                "Checkpoint expected_idea must be a string."
            )

        if not isinstance(concept_id, str):
            raise ValueError(
                "Checkpoint concept_id must be a string."
            )

        return cls(
            question=question,
            expected_idea=expected_idea,
            concept_id=concept_id,
        )


# ============================================================
# LESSON SECTION
# ============================================================

@dataclass
class LessonSection:
    section_id: str
    heading: str
    purpose: str
    explanation: str

    intuition: str = ""
    analogy: str = ""
    formula_explanation: str = ""
    derivation: str = ""

    worked_examples: list[WorkedExample] = field(
        default_factory=list
    )

    common_mistakes: list[str] = field(
        default_factory=list
    )

    retrieval_checkpoint: RetrievalCheckpoint | None = None

    concept_ids: list[str] = field(
        default_factory=list
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "section_id": self.section_id,
            "heading": self.heading,
            "purpose": self.purpose,
            "explanation": self.explanation,
            "intuition": self.intuition,
            "analogy": self.analogy,
            "formula_explanation": self.formula_explanation,
            "derivation": self.derivation,
            "worked_examples": [
                example.to_dict()
                for example in self.worked_examples
            ],
            "common_mistakes": self.common_mistakes,
            "retrieval_checkpoint": (
                self.retrieval_checkpoint.to_dict()
                if self.retrieval_checkpoint
                else None
            ),
            "concept_ids": self.concept_ids,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LessonSection":
        if not isinstance(data, dict):
            raise ValueError(
                "LessonSection must be a dictionary."
            )

        required_fields = [
            "section_id",
            "heading",
            "purpose",
            "explanation",
        ]

        missing = [
            field_name
            for field_name in required_fields
            if field_name not in data
        ]

        if missing:
            raise ValueError(
                f"LessonSection missing fields: {missing}"
            )

        for field_name in required_fields:
            if (
                not isinstance(data[field_name], str)
                or not data[field_name].strip()
            ):
                raise ValueError(
                    f"LessonSection '{field_name}' "
                    "must be a non-empty string."
                )

        worked_examples_data = data.get("worked_examples", [])

        if not isinstance(worked_examples_data, list):
            raise ValueError(
                "worked_examples must be a list."
            )

        worked_examples = [
            WorkedExample.from_dict(example)
            for example in worked_examples_data
        ]

        common_mistakes = data.get("common_mistakes", [])

        if not isinstance(common_mistakes, list):
            raise ValueError(
                "common_mistakes must be a list."
            )

        if not all(
            isinstance(mistake, str)
            for mistake in common_mistakes
        ):
            raise ValueError(
                "Every common mistake must be a string."
            )

        checkpoint_data = data.get("retrieval_checkpoint")

        checkpoint = None

        if checkpoint_data is not None:
            checkpoint = RetrievalCheckpoint.from_dict(
                checkpoint_data
            )

        concept_ids = data.get("concept_ids", [])

        if not isinstance(concept_ids, list):
            raise ValueError(
                "concept_ids must be a list."
            )

        if not all(
            isinstance(concept_id, str)
            for concept_id in concept_ids
        ):
            raise ValueError(
                "Every concept_id must be a string."
            )

        return cls(
            section_id=data["section_id"],
            heading=data["heading"],
            purpose=data["purpose"],
            explanation=data["explanation"],
            intuition=data.get("intuition", ""),
            analogy=data.get("analogy", ""),
            formula_explanation=data.get(
                "formula_explanation",
                "",
            ),
            derivation=data.get("derivation", ""),
            worked_examples=worked_examples,
            common_mistakes=common_mistakes,
            retrieval_checkpoint=checkpoint,
            concept_ids=concept_ids,
        )


# ============================================================
# COMPLETE LESSON DOCUMENT
# ============================================================

@dataclass
class LessonDocument:
    topic: str
    subject: str
    academic_level: str
    difficulty: str

    title: str
    introduction: str

    learning_objectives: list[str] = field(
        default_factory=list
    )

    prerequisites: list[str] = field(
        default_factory=list
    )

    sections: list[LessonSection] = field(
        default_factory=list
    )

    final_summary: list[str] = field(
        default_factory=list
    )

    quiz_metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic": self.topic,
            "subject": self.subject,
            "academic_level": self.academic_level,
            "difficulty": self.difficulty,
            "title": self.title,
            "introduction": self.introduction,
            "learning_objectives": self.learning_objectives,
            "prerequisites": self.prerequisites,
            "sections": [
                section.to_dict()
                for section in self.sections
            ],
            "final_summary": self.final_summary,
            "quiz_metadata": self.quiz_metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LessonDocument":
        if not isinstance(data, dict):
            raise ValueError(
                "LessonDocument must be a dictionary."
            )

        required_fields = [
            "topic",
            "subject",
            "academic_level",
            "difficulty",
            "title",
            "introduction",
            "learning_objectives",
            "prerequisites",
            "sections",
            "final_summary",
            "quiz_metadata",
        ]

        missing = [
            field_name
            for field_name in required_fields
            if field_name not in data
        ]

        if missing:
            raise ValueError(
                f"LessonDocument missing fields: {missing}"
            )

        string_fields = [
            "topic",
            "subject",
            "academic_level",
            "difficulty",
            "title",
            "introduction",
        ]

        for field_name in string_fields:
            if not isinstance(data[field_name], str):
                raise ValueError(
                    f"LessonDocument '{field_name}' "
                    "must be a string."
                )

        list_fields = [
            "learning_objectives",
            "prerequisites",
            "sections",
            "final_summary",
        ]

        for field_name in list_fields:
            if not isinstance(data[field_name], list):
                raise ValueError(
                    f"LessonDocument '{field_name}' "
                    "must be a list."
                )

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
            isinstance(item, str)
            for item in data["final_summary"]
        ):
            raise ValueError(
                "Every final summary item must be a string."
            )

        sections = [
            LessonSection.from_dict(section)
            for section in data["sections"]
        ]

        if not sections:
            raise ValueError(
                "LessonDocument must contain at least one section."
            )

        if not isinstance(data["quiz_metadata"], dict):
            raise ValueError(
                "quiz_metadata must be a dictionary."
            )

        return cls(
            topic=data["topic"],
            subject=data["subject"],
            academic_level=data["academic_level"],
            difficulty=data["difficulty"],
            title=data["title"],
            introduction=data["introduction"],
            learning_objectives=data["learning_objectives"],
            prerequisites=data["prerequisites"],
            sections=sections,
            final_summary=data["final_summary"],
            quiz_metadata=data["quiz_metadata"],
        )