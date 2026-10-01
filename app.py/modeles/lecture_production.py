from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ============================================================
# HELPER FUNCTIONS                                            
# ============================================================

def _as_string(value: Any, default: str = "") -> str:
    """
    Convert a value into a string safely.
    """

    if value is None:
        return default

    if isinstance(value, str):
        return value.strip()

    return str(value).strip()


def _as_string_list(value: Any) -> list[str]:
    """
    Convert a value into a list of strings.

    Accepted inputs:
    - None
    - one string
    - list/tuple of values
    """

    if value is None:
        return []

    if isinstance(value, str):
        cleaned = value.strip()

        if not cleaned:
            return []

        return [cleaned]

    if isinstance(value, (list, tuple)):
        result = []

        for item in value:
            text = _as_string(item)

            if text:
                result.append(text)

        return result

    return [_as_string(value)]


def _as_dict(value: Any) -> dict[str, Any]:
    """
    Convert a value into a dictionary safely.
    """

    if isinstance(value, dict):
        return value

    return {}


def _get_first(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Return the first available key from a dictionary.

    This helps when the AI uses slightly different key names.
    """

    for key in keys:
        if key in data:
            return data[key]

    return default


# ============================================================
# FORMULA MODEL
# ============================================================

@dataclass
class FormulaBlock:
    """
    Represents one important formula in the textbook lesson.
    """

    name: str
    formula: str
    explanation: str = ""
    symbols: dict[str, str] = field(default_factory=dict)
    units: dict[str, str] = field(default_factory=dict)
    conditions: list[str] = field(default_factory=list)
    derivation: str = ""
    usage: str = ""
    common_mistakes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Any) -> "FormulaBlock":
        """
        Create a FormulaBlock from AI-generated JSON.
        """

        data = _as_dict(data)

        symbols = _as_dict(
            _get_first(
                data,
                "symbols",
                "symbol_meanings",
                "variables",
                default={},
            )
        )

        units = _as_dict(
            _get_first(
                data,
                "units",
                "symbol_units",
                default={},
            )
        )

        return cls(
            name=_as_string(
                _get_first(
                    data,
                    "name",
                    "title",
                    "formula_name",
                    default="Important Formula",
                )
            ),
            formula=_as_string(
                _get_first(
                    data,
                    "formula",
                    "equation",
                    "expression",
                    default="",
                )
            ),
            explanation=_as_string(
                _get_first(
                    data,
                    "explanation",
                    "meaning",
                    default="",
                )
            ),
            symbols={
                _as_string(key): _as_string(value)
                for key, value in symbols.items()
            },
            units={
                _as_string(key): _as_string(value)
                for key, value in units.items()
            },
            conditions=_as_string_list(
                _get_first(
                    data,
                    "conditions",
                    "valid_when",
                    default=[],
                )
            ),
            derivation=_as_string(
                _get_first(
                    data,
                    "derivation",
                    "derivation_steps",
                    default="",
                )
            ),
            usage=_as_string(
                _get_first(
                    data,
                    "usage",
                    "when_to_use",
                    "application",
                    default="",
                )
            ),
            common_mistakes=_as_string_list(
                _get_first(
                    data,
                    "common_mistakes",
                    "mistakes",
                    default=[],
                )
            ),
        )


# ============================================================
# SOLVED EXAMPLE MODEL
# ============================================================

@dataclass
class SolvedExample:
    """
    Represents one solved example in the textbook lesson.
    """

    title: str
    question: str
    given: list[str] = field(default_factory=list)
    approach: str = ""
    steps: list[str] = field(default_factory=list)
    final_answer: str = ""
    explanation: str = ""
    common_mistake: str = ""

    @classmethod
    def from_dict(cls, data: Any) -> "SolvedExample":
        """
        Create a SolvedExample from AI-generated JSON.
        """

        data = _as_dict(data)

        return cls(
            title=_as_string(
                _get_first(
                    data,
                    "title",
                    "name",
                    default="Solved Example",
                )
            ),
            question=_as_string(
                _get_first(
                    data,
                    "question",
                    "problem",
                    default="",
                )
            ),
            given=_as_string_list(
                _get_first(
                    data,
                    "given",
                    "given_data",
                    "known_values",
                    default=[],
                )
            ),
            approach=_as_string(
                _get_first(
                    data,
                    "approach",
                    "method",
                    default="",
                )
            ),
            steps=_as_string_list(
                _get_first(
                    data,
                    "steps",
                    "solution_steps",
                    default=[],
                )
            ),
            final_answer=_as_string(
                _get_first(
                    data,
                    "final_answer",
                    "answer",
                    "result",
                    default="",
                )
            ),
            explanation=_as_string(
                _get_first(
                    data,
                    "explanation",
                    "reasoning",
                    default="",
                )
            ),
            common_mistake=_as_string(
                _get_first(
                    data,
                    "common_mistake",
                    "common_error",
                    default="",
                )
            ),
        )


# ============================================================
# VISUAL REQUIREMENT MODEL
# ============================================================

@dataclass
class VisualRequirement:
    """
    Represents a diagram, image, table, graph, or other visual
    needed to understand a textbook section.

    This model only describes the visual requirement.
    It does not download or generate the image.
    """

    visual_id: str
    visual_type: str
    title: str
    description: str
    purpose: str = ""
    placement: str = "beside_explanation"
    caption: str = ""
    search_query: str = ""
    preferred_source: str = ""
    license_requirement: str = ""
    attribution_required: bool = True
    labels: list[str] = field(default_factory=list)
    related_concept: str = ""

    @classmethod
    def from_dict(cls, data: Any) -> "VisualRequirement":
        """
        Create a VisualRequirement from AI-generated JSON.
        """

        data = _as_dict(data)

        attribution_value = _get_first(
            data,
            "attribution_required",
            "needs_attribution",
            default=True,
        )

        if isinstance(attribution_value, str):
            attribution_required = (
                attribution_value.lower()
                not in {"false", "no", "not required", "0"}
            )
        else:
            attribution_required = bool(attribution_value)

        return cls(
            visual_id=_as_string(
                _get_first(
                    data,
                    "visual_id",
                    "id",
                    default="visual_001",
                )
            ),
            visual_type=_as_string(
                _get_first(
                    data,
                    "visual_type",
                    "type",
                    default="diagram",
                )
            ),
            title=_as_string(
                _get_first(
                    data,
                    "title",
                    "name",
                    default="Educational Visual",
                )
            ),
            description=_as_string(
                _get_first(
                    data,
                    "description",
                    "what_to_show",
                    default="",
                )
            ),
            purpose=_as_string(
                _get_first(
                    data,
                    "purpose",
                    "why_needed",
                    default="",
                )
            ),
            placement=_as_string(
                _get_first(
                    data,
                    "placement",
                    "position",
                    default="beside_explanation",
                )
            ),
            caption=_as_string(
                _get_first(
                    data,
                    "caption",
                    default="",
                )
            ),
            search_query=_as_string(
                _get_first(
                    data,
                    "search_query",
                    "image_search_query",
                    default="",
                )
            ),
            preferred_source=_as_string(
                _get_first(
                    data,
                    "preferred_source",
                    "source",
                    default="Wikimedia Commons",
                )
            ),
            license_requirement=_as_string(
                _get_first(
                    data,
                    "license_requirement",
                    "license",
                    default="Open license or public domain",
                )
            ),
            attribution_required=attribution_required,
            labels=_as_string_list(
                _get_first(
                    data,
                    "labels",
                    "required_labels",
                    default=[],
                )
            ),
            related_concept=_as_string(
                _get_first(
                    data,
                    "related_concept",
                    "concept",
                    default="",
                )
            ),
        )


# ============================================================
# PRACTICE QUESTION MODEL
# ============================================================

@dataclass
class PracticeQuestion:
    """
    Represents a question for active recall and practice.
    """

    question: str
    question_type: str = "short_answer"
    difficulty: str = "standard"
    expected_answer: str = ""
    explanation: str = ""
    hints: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Any) -> "PracticeQuestion":
        """
        Create a PracticeQuestion from AI-generated JSON.
        """

        data = _as_dict(data)

        return cls(
            question=_as_string(
                _get_first(
                    data,
                    "question",
                    "prompt",
                    default="",
                )
            ),
            question_type=_as_string(
                _get_first(
                    data,
                    "question_type",
                    "type",
                    default="short_answer",
                )
            ),
            difficulty=_as_string(
                _get_first(
                    data,
                    "difficulty",
                    default="standard",
                )
            ),
            expected_answer=_as_string(
                _get_first(
                    data,
                    "expected_answer",
                    "answer",
                    "solution",
                    default="",
                )
            ),
            explanation=_as_string(
                _get_first(
                    data,
                    "explanation",
                    "solution_explanation",
                    default="",
                )
            ),
            hints=_as_string_list(
                _get_first(
                    data,
                    "hints",
                    default=[],
                )
            ),
        )


# ============================================================
# TEXTBOOK SECTION MODEL
# ============================================================

@dataclass
class TextbookSection:
    """
    Represents one complete section of a textbook chapter.
    """

    section_id: str
    heading: str
    concept: str
    objective: str
    explanation: str

    key_definitions: list[str] = field(default_factory=list)
    intuition: str = ""
    formulas: list[FormulaBlock] = field(default_factory=list)
    solved_examples: list[SolvedExample] = field(default_factory=list)
    visual_requirements: list[VisualRequirement] = field(
        default_factory=list
    )
    comparison_table: list[dict[str, str]] = field(
        default_factory=list
    )
    key_points: list[str] = field(default_factory=list)
    common_misconceptions: list[str] = field(
        default_factory=list
    )
    practice_questions: list[PracticeQuestion] = field(
        default_factory=list
    )
    section_summary: str = ""

    @classmethod
    def from_dict(cls, data: Any, index: int = 1) -> "TextbookSection":
        """
        Create a TextbookSection from AI-generated JSON.
        """

        data = _as_dict(data)

        formulas_data = _get_first(
            data,
            "formulas",
            "formula_blocks",
            default=[],
        )

        examples_data = _get_first(
            data,
            "solved_examples",
            "examples",
            default=[],
        )

        visuals_data = _get_first(
            data,
            "visual_requirements",
            "visuals",
            "images",
            default=[],
        )

        questions_data = _get_first(
            data,
            "practice_questions",
            "questions",
            default=[],
        )

        table_data = _get_first(
            data,
            "comparison_table",
            "comparison",
            "table",
            default=[],
        )

        if not isinstance(formulas_data, list):
            formulas_data = []

        if not isinstance(examples_data, list):
            examples_data = []

        if not isinstance(visuals_data, list):
            visuals_data = []

        if not isinstance(questions_data, list):
            questions_data = []

        if not isinstance(table_data, list):
            table_data = []

        comparison_table = []

        for row in table_data:
            if isinstance(row, dict):
                comparison_table.append(
                    {
                        _as_string(key): _as_string(value)
                        for key, value in row.items()
                    }
                )

        return cls(
            section_id=_as_string(
                _get_first(
                    data,
                    "section_id",
                    "id",
                    default=f"section_{index:03d}",
                )
            ),
            heading=_as_string(
                _get_first(
                    data,
                    "heading",
                    "title",
                    default=f"Section {index}",
                )
            ),
            concept=_as_string(
                _get_first(
                    data,
                    "concept",
                    "main_concept",
                    default="",
                )
            ),
            objective=_as_string(
                _get_first(
                    data,
                    "objective",
                    "learning_objective",
                    default="",
                )
            ),
            explanation=_as_string(
                _get_first(
                    data,
                    "explanation",
                    "content",
                    "main_explanation",
                    default="",
                )
            ),
            key_definitions=_as_string_list(
                _get_first(
                    data,
                    "key_definitions",
                    "definitions",
                    default=[],
                )
            ),
            intuition=_as_string(
                _get_first(
                    data,
                    "intuition",
                    "simple_intuition",
                    default="",
                )
            ),
            formulas=[
                FormulaBlock.from_dict(item)
                for item in formulas_data
            ],
            solved_examples=[
                SolvedExample.from_dict(item)
                for item in examples_data
            ],
            visual_requirements=[
                VisualRequirement.from_dict(item)
                for item in visuals_data
            ],
            comparison_table=comparison_table,
            key_points=_as_string_list(
                _get_first(
                    data,
                    "key_points",
                    "important_points",
                    default=[],
                )
            ),
            common_misconceptions=_as_string_list(
                _get_first(
                    data,
                    "common_misconceptions",
                    "misconceptions",
                    "common_mistakes",
                    default=[],
                )
            ),
            practice_questions=[
                PracticeQuestion.from_dict(item)
                for item in questions_data
            ],
            section_summary=_as_string(
                _get_first(
                    data,
                    "section_summary",
                    "summary",
                    default="",
                )
            ),
        )


# ============================================================
# COMPLETE TEXTBOOK LESSON MODEL
# ============================================================

@dataclass
class TextbookLessonPlan:
    """
    Complete textbook-style lesson plan.

    This is the main output of the lecture production planner.

    It contains:
    - readable explanations
    - definitions
    - formulas
    - solved examples
    - textbook visuals
    - comparisons
    - practice questions
    - final summary

    It does not contain:
    - narration timing
    - scene duration
    - video timing
    - TTS information
    - MP4 instructions
    """

    topic: str
    subject: str
    academic_level: str
    difficulty: str

    title: str
    introduction: str
    learning_objectives: list[str]

    sections: list[TextbookSection] = field(
        default_factory=list
    )

    prerequisites: list[str] = field(
        default_factory=list
    )

    important_formulas: list[FormulaBlock] = field(
        default_factory=list
    )

    real_life_connections: list[str] = field(
        default_factory=list
    )

    common_misconceptions: list[str] = field(
        default_factory=list
    )

    final_summary: list[str] = field(
        default_factory=list
    )

    revision_sheet: list[str] = field(
        default_factory=list
    )

    practice_questions: list[PracticeQuestion] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(cls, data: Any) -> "TextbookLessonPlan":
        """
        Convert AI-generated JSON into a TextbookLessonPlan.

        This method is intentionally tolerant because AI output
        may sometimes use slightly different field names.
        """

        data = _as_dict(data)

        sections_data = _get_first(
            data,
            "sections",
            "textbook_sections",
            "lesson_sections",
            default=[],
        )

        formulas_data = _get_first(
            data,
            "important_formulas",
            "formulas",
            "formula_summary",
            default=[],
        )

        questions_data = _get_first(
            data,
            "practice_questions",
            "questions",
            default=[],
        )

        if not isinstance(sections_data, list):
            sections_data = []

        if not isinstance(formulas_data, list):
            formulas_data = []

        if not isinstance(questions_data, list):
            questions_data = []

        topic = _as_string(
            _get_first(
                data,
                "topic",
                default="",
            )
        )

        subject = _as_string(
            _get_first(
                data,
                "subject",
                default="",
            )
        )

        academic_level = _as_string(
            _get_first(
                data,
                "academic_level",
                "grade_level",
                "level",
                default="",
            )
        )

        difficulty = _as_string(
            _get_first(
                data,
                "difficulty",
                default="standard",
            )
        )

        title = _as_string(
            _get_first(
                data,
                "title",
                "lesson_title",
                default=topic,
            )
        )

        return cls(
            topic=topic,
            subject=subject,
            academic_level=academic_level,
            difficulty=difficulty,
            title=title,
            introduction=_as_string(
                _get_first(
                    data,
                    "introduction",
                    "intro",
                    "overview",
                    default="",
                )
            ),
            learning_objectives=_as_string_list(
                _get_first(
                    data,
                    "learning_objectives",
                    "objectives",
                    "goals",
                    default=[],
                )
            ),
            sections=[
                TextbookSection.from_dict(
                    item,
                    index=index,
                )
                for index, item in enumerate(
                    sections_data,
                    start=1,
                )
            ],
            prerequisites=_as_string_list(
                _get_first(
                    data,
                    "prerequisites",
                    "required_knowledge",
                    default=[],
                )
            ),
            important_formulas=[
                FormulaBlock.from_dict(item)
                for item in formulas_data
            ],
            real_life_connections=_as_string_list(
                _get_first(
                    data,
                    "real_life_connections",
                    "applications",
                    "real_world_connections",
                    default=[],
                )
            ),
            common_misconceptions=_as_string_list(
                _get_first(
                    data,
                    "common_misconceptions",
                    "misconceptions",
                    "common_mistakes",
                    default=[],
                )
            ),
            final_summary=_as_string_list(
                _get_first(
                    data,
                    "final_summary",
                    "summary",
                    "key_takeaways",
                    default=[],
                )
            ),
            revision_sheet=_as_string_list(
                _get_first(
                    data,
                    "revision_sheet",
                    "quick_revision",
                    "revision_points",
                    default=[],
                )
            ),
            practice_questions=[
                PracticeQuestion.from_dict(item)
                for item in questions_data
            ],
            metadata=_as_dict(
                _get_first(
                    data,
                    "metadata",
                    default={},
                )
            ),
        )

    def total_formula_count(self) -> int:
        """
        Return the total number of formulas in the lesson.

        This includes:
        - formulas listed at lesson level
        - formulas inside individual sections
        """

        section_formula_count = sum(
            len(section.formulas)
            for section in self.sections
        )

        return len(self.important_formulas) + section_formula_count

    def total_visual_count(self) -> int:
        """
        Return the total number of visual requirements.
        """

        return sum(
            len(section.visual_requirements)
            for section in self.sections
        )

    def total_practice_question_count(self) -> int:
        """
        Return the total number of practice questions.

        This includes:
        - lesson-level practice questions
        - section-level practice questions
        """

        section_question_count = sum(
            len(section.practice_questions)
            for section in self.sections
        )

        return (
            len(self.practice_questions)
            + section_question_count
        )


    