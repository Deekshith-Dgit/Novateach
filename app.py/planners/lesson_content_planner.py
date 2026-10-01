from typing import Any

from ai_generator import generate_with_ai

from modeles.lesson_plan import LearningBlueprint
from modeles.lesson_content import LessonDocument


# ============================================================
# PROFILE EXTRACTION
# ============================================================

def get_profile_context(
    learner_profile: Any,
) -> dict:
    """
    Extract only useful learning-related information from the
    learner profile.

    Supports both:
    1. the newer adaptive learner-context dictionary
    2. the older learner profile object
    """

    if learner_profile is None:
        return {}

    # New adaptive learner context.
    if isinstance(learner_profile, dict):
        return {
            "learner_profile": learner_profile.get(
                "learner_profile",
                {},
            ),
            "weak_concepts": learner_profile.get(
                "weak_concepts",
                [],
            ),
            "active_error_patterns": learner_profile.get(
                "active_error_patterns",
                [],
            ),
            "skill_estimates": learner_profile.get(
                "skill_estimates",
                [],
            ),
            "recommended_action": learner_profile.get(
                "recommended_action",
                "continue_learning",
            ),
            "adaptation_reason": learner_profile.get(
                "adaptation_reason",
                "",
            ),
        }

    profile_fields = [
        "profile_summary",
        "understanding_strategy",
        "support_strategy",
        "retention_pattern",
        "pace_preference",
        "teaching_strategy",
        "learning_style",
        "confusion_pattern",
        "difficulty_trigger",
        "learning_goal",
        "confidence_level",
        "interest_area",
        "free_text_learning_signals",
    ]

    context = {}

    for field_name in profile_fields:
        value = getattr(
            learner_profile,
            field_name,
            None,
        )

        if value is not None:
            context[field_name] = value

    return context


# ============================================================
# SEMANTIC TOPIC PROFILE
# ============================================================

def get_topic_profile(
    blueprint: LearningBlueprint,
) -> dict[str, Any]:
    """
    Extract the authoritative semantic topic profile from
    the LearningBlueprint.

    The profile originates from the Topic Resolver and is
    treated as the content-boundary contract for generation.
    """

    topic_profile = getattr(
        blueprint,
        "topic_profile",
        None,
    )

    if not isinstance(topic_profile, dict):
        return {
            "domain": "",
            "topic_type": "",
            "content_modes": [],
            "formula_relevant": None,
            "quantitative_relevant": None,
        }

    content_modes = topic_profile.get(
        "content_modes",
        [],
    )

    if not isinstance(content_modes, list):
        content_modes = []

    cleaned_content_modes = [
        item.strip()
        for item in content_modes
        if isinstance(item, str) and item.strip()
    ]

    formula_relevant = topic_profile.get(
        "formula_relevant",
    )

    if not isinstance(formula_relevant, bool):
        formula_relevant = None

    quantitative_relevant = topic_profile.get(
        "quantitative_relevant",
    )

    if not isinstance(quantitative_relevant, bool):
        quantitative_relevant = None

    return {
        "domain": str(
            topic_profile.get(
                "domain",
                "",
            )
        ).strip(),
        "topic_type": str(
            topic_profile.get(
                "topic_type",
                "",
            )
        ).strip(),
        "content_modes": cleaned_content_modes,
        "formula_relevant": formula_relevant,
        "quantitative_relevant": quantitative_relevant,
    }


# ============================================================
# SEMANTIC CONSTRAINT VALIDATION
# ============================================================

def validate_semantic_constraints(
    data: dict,
    topic_profile: dict[str, Any],
) -> None:
    """
    Deterministically enforce the most important semantic
    constraints after AI generation.

    The AI is responsible for generating the lesson.

    This function is the final safety boundary that prevents
    schema fields from overriding the Topic Resolver.
    """

    formula_relevant = topic_profile.get(
        "formula_relevant"
    )

    quantitative_relevant = topic_profile.get(
        "quantitative_relevant"
    )

    sections = data.get(
        "sections",
        [],
    )

    if not isinstance(sections, list):
        return

    # --------------------------------------------------------
    # Formula boundary
    # --------------------------------------------------------

    if formula_relevant is False:

        for index, section in enumerate(sections):

            if not isinstance(section, dict):
                continue

            formula_explanation = section.get(
                "formula_explanation",
                "",
            )

            derivation = section.get(
                "derivation",
                "",
            )

            if formula_explanation not in ("", None):
                raise ValueError(
                    "Semantic topic violation: "
                    f"section {index + 1} contains "
                    "formula_explanation even though "
                    "formula_relevant=False."
                )

            if derivation not in ("", None):
                raise ValueError(
                    "Semantic topic violation: "
                    f"section {index + 1} contains "
                    "derivation even though "
                    "formula_relevant=False."
                )

    # --------------------------------------------------------
    # Quantitative boundary
    # --------------------------------------------------------

    if quantitative_relevant is False:

        for index, section in enumerate(sections):

            if not isinstance(section, dict):
                continue

            worked_examples = section.get(
                "worked_examples",
                [],
            )

            if not isinstance(
                worked_examples,
                list,
            ):
                continue

            # We do not reject ordinary examples here.
            #
            # The generator may use conceptual scenarios,
            # behavioural examples, case studies, etc.
            #
            # Quantitative relevance controls whether numerical
            # calculation is a core method, rather than banning
            # every number that might naturally occur in prose.


# ============================================================
# PROMPT BUILDER
# ============================================================

def build_lesson_content_prompt(
    blueprint: LearningBlueprint,
    learner_profile: Any = None,
) -> str:
    """
    Build the prompt for generating the actual student-facing
    lesson from the personalized LearningBlueprint.
    """

    profile_context = get_profile_context(
        learner_profile,
    )

    blueprint_data = blueprint.to_dict()

    # IMPORTANT:
    # topic_profile is extracted separately because the current
    # LearningBlueprint model may not serialize this dynamic
    # attribute through to_dict().

    topic_profile = get_topic_profile(
        blueprint,
    )

    return f"""
You are an expert teacher and educational content designer.

Create a deep-understanding text lesson for a student.

The lesson must be generated from the provided personalized
LearningBlueprint.

Do not ignore the blueprint.

============================================================
LEARNING BLUEPRINT
============================================================

{blueprint_data}

============================================================
AUTHORITATIVE SEMANTIC TOPIC PROFILE
============================================================

The Topic Resolver classified this topic before lesson
planning.

This profile is authoritative.

{topic_profile}

The semantic topic profile defines the educational boundary
of the requested topic.

It specifies:

- the domain
- the topic type
- appropriate content modes
- whether formulas are relevant
- whether quantitative treatment is relevant

Do NOT reconstruct, override, or reinterpret this profile.

============================================================
SEMANTIC CONTENT CONTRACT
============================================================

The semantic profile is a HARD CONTENT CONSTRAINT.

The subject name alone is NEVER sufficient to determine
the teaching method.

The topic itself determines what kind of content belongs.

Respect all of:

- domain
- topic_type
- content_modes
- formula_relevant
- quantitative_relevant

------------------------------------------------------------
FORMULA RULE
------------------------------------------------------------

If:

formula_relevant = false

then:

- DO NOT generate formulas.
- DO NOT generate derivations.
- DO NOT generate equation-based explanations.
- DO NOT generate formula-based worked examples.
- DO NOT force mathematical notation into the lesson.
- formula_explanation MUST be an empty string.
- derivation MUST be an empty string.

If:

formula_relevant = true

formulas may be used only when they genuinely belong to the
specific topic.

Never infer formula relevance merely from the subject.

For example:

Physics does NOT automatically mean formulas.

Psychology does NOT automatically mean formulas.

Computer Science does NOT automatically mean formulas.

Mathematics does NOT mean every topic requires the same
mathematical treatment.

------------------------------------------------------------
QUANTITATIVE RULE
------------------------------------------------------------

If:

quantitative_relevant = false

then:

- numerical calculation must NOT be a core teaching method
- calculation-based worked examples must NOT be used
- prefer conceptual reasoning
- prefer definitions
- prefer theories
- prefer mechanisms
- prefer scenarios
- prefer case studies
- prefer comparisons
- prefer examples

when those modes are present in content_modes.

If:

quantitative_relevant = true

quantitative reasoning may be used when it genuinely
supports the requested concepts.

============================================================
CONTENT MODE CONTRACT
============================================================

Use content_modes to determine the natural ways this topic
should be taught.

Possible modes include:

- concepts
- definitions
- theories
- mechanisms
- examples
- scenarios
- case_studies
- comparisons
- principles
- equations
- applications
- procedures
- patterns

Do NOT force every mode into the lesson.

Only use modes that genuinely belong to this topic.

============================================================
LEARNER PROFILE
============================================================

{profile_context}

The learner profile determines HOW the content should be
explained.

It does NOT determine the academic truth of the content.

Personalize:

- explanation style
- intuition
- examples
- pacing
- retrieval
- reinforcement
- misconception prevention

Do not change factual content merely to satisfy a learner
preference.

============================================================
YOUR TASK
============================================================

Generate a complete student-facing lesson.

The LearningBlueprint decides:

- what concepts must be taught
- the order of concepts
- learning objectives
- prerequisites
- teaching strategy

The semantic topic profile decides:

- what kind of content belongs
- which content modes are appropriate
- whether formulas belong
- whether quantitative treatment belongs

The learner profile decides:

- how explanations should be phrased
- how much intuition and analogy to provide
- how examples should be used
- how confusion should be prevented
- how retrieval checkpoints should appear
- how quickly difficulty should increase

============================================================
TEACHING REQUIREMENTS
============================================================

The lesson should contain:

1. A clear and engaging title.

2. An introduction or hook explaining:

   - why the topic matters
   - where it appears in real life, science, society,
     or applications when relevant
   - what the student will understand by the end

3. Learning objectives taken from the blueprint.

4. Prerequisites taken from the blueprint.

5. Multiple logically ordered sections.

Each section should contain:

- section_id
- heading
- purpose
- explanation
- intuition
- analogy
- formula_explanation
- derivation
- worked_examples
- common_mistakes
- retrieval_checkpoint
- concept_ids

Use only fields that are genuinely relevant.

A schema field existing does NOT mean it must contain
content.

Examples:

- A conceptual topic may have no formula explanation.
- A conceptual topic may have no derivation.
- A non-quantitative topic may have no numerical example.
- An analogy should be omitted when it would create confusion.

============================================================
EXPLANATION QUALITY
============================================================

Follow this order whenever appropriate:

1. Intuition before formal definition.
2. Simple explanation before technical language.
3. Define every important technical term.
4. Explain symbols and units only when formulas genuinely
   belong to the topic.
5. Show thinking processes in worked examples when examples
   are appropriate.
6. Explain why each step is taken.
7. Mention common misconceptions.
8. Connect the current concept with previous concepts.
9. Include retrieval checkpoints that test understanding,
   not just memorization.

Do not write generic textbook filler.

Do not write a video script.

Do not include:

- narration
- scene numbers
- visual plans
- video durations
- camera directions
- animation instructions
- image-generation instructions
- TTS instructions

============================================================
FINAL SEMANTIC CHECK
============================================================

Before returning JSON, internally verify:

- Does every section belong to the requested topic?
- Does the lesson match the domain?
- Does the lesson match topic_type?
- Are selected content modes appropriate?
- Did formulas appear only when formula_relevant allows them?
- Did numerical work appear only when quantitative_relevant
  allows it?
- Did any formula appear merely because the schema allowed it?

If formula_relevant is false:

formula_explanation MUST be empty.

derivation MUST be empty.

No section should teach equations or formulas.

If quantitative_relevant is false:

Numerical calculation must NOT be a core teaching method.

============================================================
OUTPUT FORMAT
============================================================
These two fields are mandatory. Never omit them, even if
their values are empty arrays or a minimal valid dictionary.

"final_summary" must always be a list.

"quiz_metadata" must always be an object containing:
- concepts
- important_ideas
- suggested_question_types
- difficulty
- misconceptions_to_test

Return ONLY valid JSON.

The JSON must follow this exact structure:

{{
    "topic": "...",
    "subject": "...",
    "academic_level": "...",
    "difficulty": "...",
    "title": "...",
    "introduction": "...",
    "learning_objectives": [],
    "prerequisites": [],
    "sections": [
        {{
            "section_id": "section_1",
            "heading": "...",
            "purpose": "...",
            "explanation": "...",
            "intuition": "...",
            "analogy": "...",
            "formula_explanation": "",
            "derivation": "",
            "worked_examples": [
                {{
                    "question": "...",
                    "thinking_steps": [],
                    "solution": "...",
                    "takeaway": "..."
                }}
            ],
            "common_mistakes": [],
            "retrieval_checkpoint": {{
                "question": "...",
                "expected_idea": "...",
                "concept_id": "..."
            }},
            "concept_ids": []
        }}
    ],
    "final_summary": [],
    "quiz_metadata": {{
        "concepts": [],
        "important_ideas": [],
        "suggested_question_types": [],
        "difficulty": "...",
        "misconceptions_to_test": []
    }}
}}

Return no Markdown.

Return no explanation outside the JSON.
"""


# ============================================================
# BASIC OUTPUT VALIDATION
# ============================================================

def validate_lesson_content_data(
    data: Any,
) -> dict:
    """
    Validate the top-level AI response before converting it
    into a LessonDocument.

    This function also normalizes simple formatting mistakes
    from the AI, such as returning final_summary as a string
    instead of a list.
    """

    if not isinstance(data, dict):
        raise ValueError(
            "Lesson content AI output must be a dictionary."
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

    missing_fields = [
        field_name
        for field_name in required_fields
        if field_name not in data
    ]

    if missing_fields:
        raise ValueError(
            f"Lesson content missing fields: {missing_fields}"
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
        value = data[field_name]

        if not isinstance(value, str):
            raise ValueError(
                f"Lesson content '{field_name}' "
                "must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"Lesson content '{field_name}' "
                "cannot be empty."
            )

    def normalize_string_list(
        value: Any,
        field_name: str,
    ) -> list[str]:
        if isinstance(value, list):
            normalized = []

            for item in value:
                if not isinstance(item, str):
                    raise ValueError(
                        f"Every item in '{field_name}' "
                        "must be a string."
                    )

                item = item.strip()

                if item:
                    normalized.append(item)

            return normalized

        if isinstance(value, str):
            lines = value.splitlines()

            normalized = [
                line.strip("- •*\t ")
                for line in lines
                if line.strip()
            ]

            if normalized:
                return normalized

            if value.strip():
                return [value.strip()]

            return []

        if isinstance(value, dict):
            normalized = []

            for item in value.values():
                if isinstance(item, str) and item.strip():
                    normalized.append(item.strip())

            return normalized

        raise ValueError(
            f"Lesson content '{field_name}' "
            "must be a list."
        )

    data["learning_objectives"] = normalize_string_list(
        data["learning_objectives"],
        "learning_objectives",
    )

    data["prerequisites"] = normalize_string_list(
        data["prerequisites"],
        "prerequisites",
    )

    if not isinstance(data["sections"], list):
        raise ValueError(
            "Lesson content 'sections' must be a list."
        )

    if not data["sections"]:
        raise ValueError(
            "Lesson content must contain at least one section."
        )

    if not isinstance(data["quiz_metadata"], dict):
        raise ValueError(
            "Lesson content 'quiz_metadata' "
            "must be a dictionary."
        )

    data["final_summary"] = normalize_string_list(
        data["final_summary"],
        "final_summary",
    )

    return data
# ============================================================
# METADATA REPAIR
# ============================================================

def repair_missing_lesson_fields(
    data: dict,
    missing_fields: list[str],
    topic_profile: dict[str, Any] | None = None,
) -> dict:
    """
    Ask the AI to provide only missing lesson metadata.

    The semantic topic profile is passed into the repair prompt
    so the repair process cannot accidentally reintroduce
    content that violates the original topic classification.
    """

    if topic_profile is None:
        topic_profile = {
            "domain": "",
            "topic_type": "",
            "content_modes": [],
            "formula_relevant": None,
            "quantitative_relevant": None,
        }

    repair_prompt = f"""
You generated a lesson JSON object, but some required
metadata fields are missing.

Do NOT rewrite the lesson.

Return ONLY valid JSON containing ONLY these missing fields.

Every requested field is mandatory.
Do not omit any requested field.

{missing_fields}

============================================================
AUTHORITATIVE SEMANTIC TOPIC PROFILE
============================================================

{topic_profile}

This profile is authoritative.

Do not introduce content that violates it.

If formula_relevant = false:

- do not introduce formulas
- do not introduce derivations
- do not introduce equation-based concepts

If quantitative_relevant = false:

- do not introduce numerical calculation as a core method

============================================================
CURRENT LESSON
============================================================

{data}

============================================================
REQUIRED FIELD RULES
============================================================

final_summary:

A concise list of the most important ideas actually taught
in the lesson.

quiz_metadata:

A dictionary containing:

{{
    "concepts": [],
    "important_ideas": [],
    "suggested_question_types": [],
    "difficulty": "...",
    "misconceptions_to_test": []
}}

The fields must be appropriate for the actual topic and
the actual lesson.

Do not invent formulas, numerical content, or concepts that
are inconsistent with the semantic topic profile.

Return ONLY valid JSON.
"""

    repaired_fields = generate_with_ai(
        repair_prompt,
        expect_json=True,
    )

    if not isinstance(repaired_fields, dict):
        raise ValueError(
            "Lesson metadata repair must return a dictionary."
        )

    repaired_data = dict(data)

    for field_name in missing_fields:

        if field_name not in repaired_fields:
            raise ValueError(
                "Lesson metadata repair failed to provide "
                f"'{field_name}'."
            )

        repaired_data[field_name] = repaired_fields[field_name]

    return repaired_data


# ============================================================
# GENERATE COMPLETE LESSON
# ============================================================

def generate_lecture(
    blueprint: LearningBlueprint,
    learner_profile: Any = None,
) -> LessonDocument:
    """
    Generate a personalized text lesson from a
    LearningBlueprint.
    """

    if not isinstance(
        blueprint,
        LearningBlueprint,
    ):
        raise TypeError(
            "generate_lecture() requires a LearningBlueprint."
        )

    topic_profile = get_topic_profile(
        blueprint,
    )

    prompt = build_lesson_content_prompt(
        blueprint=blueprint,
        learner_profile=learner_profile,
    )

    raw_result = generate_with_ai(
        prompt,
        expect_json=True,
    )

    if not isinstance(raw_result, dict):
        raise ValueError(
            "Lesson content AI output must be a dictionary."
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

    missing_fields = [
        field_name
        for field_name in required_fields
        if field_name not in raw_result
    ]

    if missing_fields:
        raw_result = repair_missing_lesson_fields(
            data=raw_result,
            missing_fields=missing_fields,
            topic_profile=topic_profile,
        )

    validated_data = validate_lesson_content_data(
        raw_result,
    )

    validate_semantic_constraints(
        validated_data,
        topic_profile,
    )

    return LessonDocument.from_dict(
        validated_data,
    )


 