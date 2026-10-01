import json

from typing import Any

from ai_generator import generate_with_ai

from modeles.lesson_plan import (
    LessonRequest,
    LearningBlueprint,
)


# ============================================================
# LEARNER CONTEXT NORMALIZATION
# ============================================================

def _prepare_learner_context(
    learner_profile: Any,
) -> dict[str, Any]:

    # New adaptive learner context
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

    # Backward compatibility with existing UserProfile object
    profile_summary = getattr(
        learner_profile,
        "profile_summary",
        None,
    )

    if not profile_summary:
        profile_summary = {
            "teaching_instructions": [
                "Use a clear and neutral teaching approach."
            ]
        }

    return {
        "learner_profile": profile_summary,
        "weak_concepts": [],
        "active_error_patterns": [],
        "skill_estimates": [],
        "recommended_action": "continue_learning",
        "adaptation_reason": "",
    }


# ============================================================
# TOPIC PROFILE NORMALIZATION
# ============================================================

def _prepare_topic_profile(
    topic_profile: Any,
) -> dict[str, Any]:
    """
    Normalize the semantic topic profile produced by the
    Topic Resolver.

    Learner context answers:

        HOW should this student be taught?

    Topic profile answers:

        WHAT kind of content belongs to this topic?
    """

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
        "formula_relevant"
    )

    if not isinstance(formula_relevant, bool):
        formula_relevant = None

    quantitative_relevant = topic_profile.get(
        "quantitative_relevant"
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
# BUILD LESSON PLANNER PROMPT
# ============================================================

def build_lesson_prompt(
    request: LessonRequest,
    learner_profile: Any,
):

    learner_context = _prepare_learner_context(
        learner_profile
    )

    topic_profile = _prepare_topic_profile(
        request.topic_profile
    )

    return f"""
You are the Lesson Planner for Novateach.

Your job is to decide WHAT the student should learn
and IN WHAT PEDAGOGICAL ORDER.

You are NOT responsible for:

- narration
- TTS
- visuals
- animations
- scene timing
- video production

Those belong to downstream systems.

==================================================
LESSON REQUEST
==================================================

Topic:

{request.topic}

Subject:

{request.subject}

Academic Level:

{request.academic_level}

Difficulty:

{request.difficulty}

IMPORTANT:

Academic level defines the educational level.

Difficulty defines the challenge level WITHIN that
academic level.

For example:

Academic Level = Class 10
Difficulty = Advanced

means advanced Class 10 content.

It does NOT mean undergraduate content.

==================================================
SEMANTIC TOPIC PROFILE
==================================================

The Topic Resolver has already analysed the meaning
and educational nature of the requested topic.

Use this profile as a HARD CONTENT BOUNDARY.

{json.dumps(topic_profile, indent=2, default=str)}

The semantic profile tells you:

- what domain the topic belongs to
- what type of topic it is
- which teaching/content modes are relevant
- whether formulas are genuinely relevant
- whether quantitative treatment is genuinely relevant

==================================================
SEMANTIC CONTENT BOUNDARY
==================================================

Follow these rules strictly.

1. Do NOT override the semantic topic profile merely
   because the subject is commonly associated with
   mathematics, science, or formulas.

2. The subject alone does NOT determine whether formulas
   belong in the lesson.

3. Use the topic_type, content_modes,
   formula_relevant, and quantitative_relevant fields
   to decide the pedagogical content.

4. If formula_relevant is false:

   - Do NOT plan formulas.
   - Do NOT plan derivations.
   - Do NOT plan numerical calculation problems.
   - Do NOT create symbolic equations merely to make
     the lesson appear rigorous.

5. If quantitative_relevant is false:

   - Do NOT make numerical problem solving a core
     learning objective.
   - Prefer conceptual reasoning, examples, scenarios,
     comparisons, mechanisms, or case studies when
     supported by content_modes.

6. If formula_relevant is true:

   - Include formulas only when they genuinely belong
     to the requested topic.
   - Do not add unrelated formulas from the wider subject.

7. If quantitative_relevant is true:

   - Quantitative reasoning may be included when it
     genuinely supports the requested concepts.

8. If the topic is mixed:

   - Separate conceptual and quantitative components.
   - Quantitative material must only appear where it
     genuinely belongs.

9. Never invent formulas merely because the output
   structure allows them.

10. The topic profile has already been semantically
    analysed upstream. Do not reinterpret the topic
    into another domain.

==================================================
CONTENT MODE RULE
==================================================

The content_modes list identifies the types of teaching
content that are naturally useful for this topic.

Prioritize the provided modes.

Examples include:

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

Do not force every possible mode into the lesson.

Use only modes that genuinely support the topic.

==================================================
ADAPTIVE LEARNER CONTEXT
==================================================

{json.dumps(learner_context, indent=2, default=str)}

The learner context contains BOTH:

1. Initial onboarding information.

2. Longitudinal evidence collected from actual learning.

Longitudinal evidence is more important for adaptation
than a single isolated response.

==================================================
LONGITUDINAL ADAPTATION RULES
==================================================

1. NEVER declare a stable learner weakness from one
   incorrect answer or one isolated mistake.

2. Treat individual mistakes as evidence, not as
   definitive learner traits.

3. Look for repeated error patterns, accumulated
   evidence, concept mastery, confidence, skill
   estimates, and recent performance before making
   strong pedagogical adaptations.

4. A recurring error pattern with supporting evidence
   may justify changing the teaching strategy.

5. If evidence is weak or insufficient, preserve the
   learner's existing teaching approach rather than
   making a strong new diagnosis.

6. Do not replace the onboarding learner profile.

   Instead, update teaching decisions using the
   accumulated learning evidence.

7. The learner's current mastery should influence
   WHAT needs reinforcement.

8. Recurring error patterns should influence HOW the
   concept is explained.

9. Skill estimates should influence the balance between
   explanation, examples, practice, reasoning, recall,
   and application.

10. Prerequisite weaknesses should influence the
    pedagogical order.

==================================================
ADAPTATION ACTIONS
==================================================

The field "recommended_action" represents the current
decision of Novateach's adaptation system.

If the action is:

"prerequisite_repair":

    Prioritize the blocking prerequisite before
    expecting strong performance on the dependent
    concept.

"targeted_practice":

    Focus the lesson on the learner's currently weak
    concept or skill while providing appropriate
    explanation and guided practice.

"retest":

    Reinforce the relevant concept and prepare the
    learner to demonstrate whether the previous
    weakness has improved.

"advance":

    Continue forward while maintaining appropriate
    reinforcement.

IMPORTANT:

Do not blindly follow the action if it conflicts with
the requested topic, semantic topic profile,
or academic scope.

==================================================
USING ERROR PATTERNS
==================================================

Error patterns are evidence about recurring difficulties.

For example:

- repeated conceptual errors
- repeated procedural errors
- repeated formula errors
- repeated prerequisite gaps
- repeated application errors

Use recurring patterns to modify teaching strategy.

Examples:

If repeated conceptual errors exist:

    increase conceptual explanation and concrete examples.

If repeated application errors exist:

    include worked examples followed by application
    practice.

If repeated prerequisite gaps exist:

    repair the prerequisite before advancing.

If evidence is insufficient:

    do not over-personalize.

IMPORTANT:

Do not introduce formula-based teaching merely because
an error pattern contains words such as "formula" if the
semantic topic profile says formulas are not relevant.

==================================================
USING SKILL ESTIMATES
==================================================

Use available skill estimates to balance the lesson.

Possible dimensions include:

- memory
- conceptual understanding
- logical thinking
- application
- pattern recognition

Do not treat one low recent result as a permanent
skill deficiency.

Use accumulated evidence and confidence when deciding
whether a skill needs additional support.

==================================================
PLANNING RULES
==================================================

1. Respect the academic level.

2. Respect the requested difficulty.

3. Respect the provided subject.

4. Respect the semantic topic profile.

5. Identify necessary prerequisites.

6. Break the topic into teachable concepts.

7. Order concepts from prerequisite →
   understanding → application.

8. Use the learner context to determine HOW
   concepts should be taught.

9. Use longitudinal evidence to adapt the lesson
   gradually rather than reacting to isolated mistakes.

10. Do not blindly follow learner preferences
    if they conflict with sound pedagogy.

11. Objectives must describe observable
    learning outcomes.

12. Do not create narration or visual instructions.

13. Do not introduce concepts outside the
    requested scope.

14. Do not change the subject provided
    in the lesson request.

15. If the learner has a relevant weak concept,
    prioritize it when appropriate.

16. If a relevant prerequisite is weak, place it
    before the dependent concept.

17. Do not introduce formulas or numerical work
    when the semantic profile marks them as
    irrelevant.

==================================================
CONCEPT STRUCTURE
==================================================

Each item in "concepts" MUST be a dictionary
with exactly these fields:

{{
    "name": "",
    "description": ""
}}

"name":

A concise name identifying the concept.

"description":

A concise explanation of what the learner
should understand about the concept.

Do NOT return concepts as plain strings.

==================================================
CONCEPT SEQUENCE
==================================================

"concept_sequence" MUST be a list of strings.

Each string MUST correspond to the "name" of
one concept in the "concepts" list.

The sequence represents the pedagogical order
in which the concepts should be learned.

==================================================
RETURN ONLY VALID JSON
==================================================

Use exactly this structure:

{{
    "topic": "",
    "subject": "",
    "academic_level": "",
    "difficulty": "",
    "learning_objectives": [
        ""
    ],
    "prerequisites": [
        ""
    ],
    "concepts": [
        {{
            "name": "",
            "description": ""
        }}
    ],
    "concept_sequence": [
        ""
    ],
    "teaching_strategy": {{
        "explanation_style": "",
        "example_strategy": "",
        "practice_strategy": "",
        "pacing_strategy": "",
        "reinforcement_strategy": ""
    }}
}}

==================================================
FINAL REQUIREMENTS
==================================================

Before returning the answer, verify that:

- "concepts" is a list.

- Every concept is a dictionary.

- Every concept contains "name" and "description".

- "concept_sequence" is a list of strings.

- Every concept_sequence item matches a concept name.

- The topic, subject, academic level, and difficulty
  match the lesson request.

- The semantic topic profile has been respected.

- If formula_relevant is false, the blueprint contains
  no formula-focused learning objective.

- If quantitative_relevant is false, the blueprint
  does not make numerical calculation a core objective.

- The lesson reflects relevant learner evidence
  without overreacting to isolated mistakes.

- The response contains ONLY valid JSON.
"""


# ============================================================
# PLAN LESSON
# ============================================================

def plan_lesson(
    topic: str,
    subject: str,
    academic_level: str,
    difficulty: str,
    learner_profile: Any,
    topic_profile: dict[str, Any] | None = None,
):
    """
    Create a LearningBlueprint.

    topic_profile comes from the Topic Resolver.

    The Topic Resolver is the source of truth for the
    semantic meaning of the topic.
    """

    normalized_topic_profile = _prepare_topic_profile(
        topic_profile
    )

    request = LessonRequest(
        topic=topic,
        subject=subject,
        academic_level=academic_level,
        difficulty=difficulty,
    )

    # --------------------------------------------------------
    # Attach the authoritative semantic profile.
    # --------------------------------------------------------
    #
    # We attach it after constructing LessonRequest so this
    # planner remains compatible with the current LessonRequest
    # model even if that dataclass has not yet been expanded.
    #
    # This gives us:
    #
    # Topic Resolver
    #       ↓
    # normalized profile
    #       ↓
    # LessonRequest
    #       ↓
    # Lesson Planner
    #
    request.topic_profile = normalized_topic_profile

    prompt = build_lesson_prompt(
        request,
        learner_profile,
    )

    def validate_blueprint(result: Any) -> None:
        if not isinstance(result, dict):
            raise ValueError(
                "Lesson Planner response must be a JSON object."
            )

        LearningBlueprint.from_dict(result)

    result = generate_with_ai(
        prompt,
        expect_json=True,
        result_validator=validate_blueprint,
    )

    blueprint = LearningBlueprint.from_dict(
        result
    )

    # --------------------------------------------------------
    # Preserve the authoritative semantic profile.
    # --------------------------------------------------------
    #
    # The AI creates the pedagogical blueprint.
    # It does NOT get to rewrite the semantic classification.
    #

    blueprint.topic_profile = normalized_topic_profile

    return blueprint