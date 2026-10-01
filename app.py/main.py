from __future__ import annotations

from typing import Any

from utils.database import create_tables

from services.auth_service import login

from services.profile_service import (
    run_onboarding,
    load_profile,
)

from services.learner_context_service import (
    get_compact_learner_context,
)

from planners.input_resolver import (
    resolve_topic,
    basic_academic_level_check,
    basic_difficulty_check,
)

from planners.lesson_planner import plan_lesson

from planners.lecture_production import (
    generate_lecture_production_plan,
)


# ============================================================
# TERMINAL DISPLAY HELPERS
# ============================================================

def print_line(
    character: str = "=",
    length: int = 80,
) -> None:
    """Print a separator line."""
    print(character * length)


def print_heading(title: str) -> None:
    """Print a major heading."""
    print()
    print_line("=")
    print(title.upper())
    print_line("=")


def print_subheading(title: str) -> None:
    """Print a smaller heading."""
    print()
    print_line("-")
    print(title)
    print_line("-")


def print_bullets(items: Any) -> None:
    """Print a list of items using bullet points."""
    if not items:
        return

    if isinstance(items, list):
        for item in items:
            print(f"• {item}")
    else:
        print(f"• {items}")


def print_numbered_items(items: Any) -> None:
    """Print a list of items using numbers."""
    if not items:
        return

    if isinstance(items, list):
        for index, item in enumerate(items, start=1):
            print(f"{index}. {item}")
    else:
        print(f"1. {items}")


# ============================================================
# FORMULA DISPLAY
# ============================================================

def print_formula(
    formula: Any,
    index: int,
) -> None:
    """Display one formula."""

    name = getattr(
        formula,
        "name",
        f"Formula {index}",
    )

    print()
    print(f"Formula {index}: {name}")

    expression = getattr(
        formula,
        "expression",
        "",
    )

    if not expression:
        expression = getattr(
            formula,
            "formula",
            "",
        )

    if expression:
        print(f"Expression: {expression}")

    explanation = getattr(
        formula,
        "explanation",
        "",
    )

    if explanation:
        print(f"Meaning: {explanation}")

    variables = getattr(
        formula,
        "variables",
        {},
    )

    if variables:
        print("Symbols:")

        if isinstance(variables, dict):
            for symbol, meaning in variables.items():
                print(f"  {symbol} = {meaning}")
        else:
            print(f"  {variables}")

    units = getattr(
        formula,
        "units",
        "",
    )

    if units:
        print(f"Units: {units}")

    conditions = getattr(
        formula,
        "conditions",
        "",
    )

    if conditions:
        print(f"Use when: {conditions}")

    derivation = getattr(
        formula,
        "derivation",
        "",
    )

    if derivation:
        print("\nDerivation:")
        print(derivation)

    example = getattr(
        formula,
        "example",
        "",
    )

    if example:
        print(f"\nExample: {example}")

    common_mistake = getattr(
        formula,
        "common_mistake",
        "",
    )

    if common_mistake:
        print(f"\nCommon mistake: {common_mistake}")


# ============================================================
# SOLVED EXAMPLE DISPLAY
# ============================================================

def print_solved_example(
    example: Any,
    index: int,
) -> None:
    """Display one solved example."""

    title = getattr(
        example,
        "title",
        f"Solved Example {index}",
    )

    print()
    print(f"Solved Example {index}: {title}")

    question = getattr(
        example,
        "question",
        "",
    )

    if question:
        print(f"\nQuestion:\n{question}")

    given = getattr(
        example,
        "given",
        "",
    )

    if given:
        print(f"\nGiven:\n{given}")

    concept_used = getattr(
        example,
        "concept_used",
        "",
    )

    if concept_used:
        print(f"\nConcept used:\n{concept_used}")

    solution_steps = getattr(
        example,
        "solution_steps",
        [],
    )

    if solution_steps:
        print("\nSolution:")

        if isinstance(solution_steps, list):
            for step_index, step in enumerate(
                solution_steps,
                start=1,
            ):
                print(f"  Step {step_index}: {step}")
        else:
            print(solution_steps)

    final_answer = getattr(
        example,
        "final_answer",
        "",
    )

    if final_answer:
        print(f"\nFinal answer:\n{final_answer}")

    takeaway = getattr(
        example,
        "takeaway",
        "",
    )

    if takeaway:
        print(f"\nTakeaway:\n{takeaway}")


# ============================================================
# VISUAL REQUIREMENT DISPLAY
# ============================================================

def print_visual_requirement(
    visual: Any,
    index: int,
) -> None:
    """Display one required visual."""

    title = getattr(
        visual,
        "title",
        f"Visual {index}",
    )

    print()
    print(f"Visual {index}: {title}")

    visual_type = getattr(
        visual,
        "visual_type",
        "",
    )

    if visual_type:
        print(f"Type: {visual_type}")

    description = getattr(
        visual,
        "description",
        "",
    )

    if description:
        print(f"Description: {description}")

    purpose = getattr(
        visual,
        "purpose",
        "",
    )

    if purpose:
        print(f"Purpose: {purpose}")

    related_concept = getattr(
        visual,
        "related_concept",
        "",
    )

    if related_concept:
        print(f"Related concept: {related_concept}")

    placement = getattr(
        visual,
        "placement",
        "",
    )

    if placement:
        print(f"Placement: {placement}")

    caption = getattr(
        visual,
        "caption",
        "",
    )

    if caption:
        print(f"Caption: {caption}")

    search_query = getattr(
        visual,
        "search_query",
        "",
    )

    if search_query:
        print(f"Image search query: {search_query}")

    preferred_source = getattr(
        visual,
        "preferred_source",
        "",
    )

    if preferred_source:
        print(f"Preferred source: {preferred_source}")

    license_requirement = getattr(
        visual,
        "license_requirement",
        "",
    )

    if license_requirement:
        print(f"License requirement: {license_requirement}")

    attribution_required = getattr(
        visual,
        "attribution_required",
        False,
    )

    print(f"Attribution required: {attribution_required}")

    labels = getattr(
        visual,
        "labels",
        [],
    )

    if labels:
        print("Labels:")
        print_bullets(labels)


# ============================================================
# TEXTBOOK SECTION DISPLAY
# ============================================================

def print_textbook_section(
    section: Any,
    index: int,
) -> None:
    """Display one textbook section."""

    title = getattr(
        section,
        "title",
        f"Section {index}",
    )

    print_heading(
        f"{index}. {title}"
    )

    explanation = getattr(
        section,
        "explanation",
        "",
    )

    if explanation:
        print_subheading("Explanation")
        print(explanation)

    intuition = getattr(
        section,
        "intuition",
        "",
    )

    if intuition:
        print_subheading("Intuition")
        print(intuition)

    definitions = getattr(
        section,
        "definitions",
        [],
    )

    if definitions:
        print_subheading("Important definitions")
        print_bullets(definitions)

    formulas = getattr(
        section,
        "formulas",
        [],
    )

    if formulas:
        print_subheading("Formulas")

        for formula_index, formula in enumerate(
            formulas,
            start=1,
        ):
            print_formula(
                formula,
                formula_index,
            )

    solved_examples = getattr(
        section,
        "solved_examples",
        [],
    )

    if solved_examples:
        print_subheading("Solved examples")

        for example_index, example in enumerate(
            solved_examples,
            start=1,
        ):
            print_solved_example(
                example,
                example_index,
            )

    visual_requirements = getattr(
        section,
        "visual_requirements",
        [],
    )

    if visual_requirements:
        print_subheading("Required visuals")

        for visual_index, visual in enumerate(
            visual_requirements,
            start=1,
        ):
            print_visual_requirement(
                visual,
                visual_index,
            )

    comparison_table = getattr(
        section,
        "comparison_table",
        "",
    )

    if comparison_table:
        print_subheading("Comparison")
        print(comparison_table)

    key_points = getattr(
        section,
        "key_points",
        [],
    )

    if key_points:
        print_subheading("Key points")
        print_bullets(key_points)

    misconceptions = getattr(
        section,
        "misconceptions",
        [],
    )

    if misconceptions:
        print_subheading("Common misconceptions")
        print_bullets(misconceptions)

    practice_questions = getattr(
        section,
        "practice_questions",
        [],
    )

    if practice_questions:
        print_subheading("Practice questions")
        print_numbered_items(practice_questions)

    summary = getattr(
        section,
        "summary",
        "",
    )

    if summary:
        print_subheading("Section summary")
        print(summary)


# ============================================================
# COMPLETE TEXTBOOK DISPLAY
# ============================================================

def print_textbook_lesson(
    lesson: Any,
) -> None:
    """Display the complete textbook lesson."""

    print_line("=")

    print(
        "NOVATEACH AI — "
        "PERSONALIZED TEXTBOOK LESSON"
    )

    print_line("=")

    title = getattr(
        lesson,
        "title",
        "",
    )

    if title:
        print(f"\nTitle: {title}")

    topic = getattr(
        lesson,
        "topic",
        "",
    )

    if topic:
        print(f"Topic: {topic}")

    subject = getattr(
        lesson,
        "subject",
        "",
    )

    if subject:
        print(f"Subject: {subject}")

    academic_level = getattr(
        lesson,
        "academic_level",
        "",
    )

    if academic_level:
        print(f"Academic level: {academic_level}")

    difficulty = getattr(
        lesson,
        "difficulty",
        "",
    )

    if difficulty:
        print(f"Difficulty: {difficulty}")

    introduction = getattr(
        lesson,
        "introduction",
        "",
    )

    if introduction:
        print_heading("Introduction")
        print(introduction)

    learning_objectives = getattr(
        lesson,
        "learning_objectives",
        [],
    )

    if learning_objectives:
        print_heading("Learning objectives")
        print_numbered_items(learning_objectives)

    prerequisites = getattr(
        lesson,
        "prerequisites",
        [],
    )

    if prerequisites:
        print_heading("Prerequisites")
        print_bullets(prerequisites)

    sections = getattr(
        lesson,
        "sections",
        [],
    )

    if sections:
        for section_index, section in enumerate(
            sections,
            start=1,
        ):
            print_textbook_section(
                section,
                section_index,
            )

    formulas = getattr(
        lesson,
        "formulas",
        [],
    )

    if formulas:
        print_heading("Complete formula sheet")

        for formula_index, formula in enumerate(
            formulas,
            start=1,
        ):
            print_formula(
                formula,
                formula_index,
            )

    real_life_connections = getattr(
        lesson,
        "real_life_connections",
        [],
    )

    if real_life_connections:
        print_heading("Real-life connections")
        print_bullets(real_life_connections)

    misconceptions = getattr(
        lesson,
        "misconceptions",
        [],
    )

    if misconceptions:
        print_heading("Important misconceptions")
        print_bullets(misconceptions)

    final_summary = getattr(
        lesson,
        "final_summary",
        "",
    )

    if final_summary:
        print_heading("Final summary")
        print(final_summary)

    revision_sheet = getattr(
        lesson,
        "revision_sheet",
        "",
    )

    if revision_sheet:
        print_heading("Revision sheet")
        print(revision_sheet)

    practice_questions = getattr(
        lesson,
        "practice_questions",
        [],
    )

    if practice_questions:
        print_heading("Final practice questions")
        print_numbered_items(practice_questions)

    print()
    print_line("=")
    print("END OF TEXTBOOK LESSON")
    print_line("=")


# ============================================================
# LESSON REQUEST
# ============================================================

def get_lesson_request() -> tuple[
    str,
    str,
    str,
    str,
]:
    """
    Collect and validate lesson input.

    Flow:
    1. Ask topic.
    2. Ask academic level.
    3. Resolve topic.
    4. If invalid, ask topic again.
    5. If ambiguous, ask subject.
    6. Ask difficulty.
    """

    print_heading(
        "Create a new lesson"
    )

    # --------------------------------------------------------
    # 1. TOPIC
    # --------------------------------------------------------

    while True:

        raw_topic = input(
            "What do you want to learn? "
        ).strip()

        if not raw_topic:
            print()
            print(
                "Topic cannot be empty. "
                "Please enter a topic again."
            )
            continue

        # ----------------------------------------------------
        # 2. ACADEMIC LEVEL
        # ----------------------------------------------------

        while True:

            academic_level = input(
                "Academic level, for example "
                "Class 10, Class 12, undergraduate: "
            ).strip()

            is_valid_level, level_message = (
                basic_academic_level_check(
                    academic_level
                )
            )

            if is_valid_level:
                break

            print()
            print(
                f"Invalid academic level: "
                f"{level_message}"
            )

        # ----------------------------------------------------
        # 3. RESOLVE TOPIC
        # ----------------------------------------------------

        try:
            topic_result = resolve_topic(
                raw_topic,
                academic_level,
            )

        except ValueError as error:
            print()
            print(
                f"Topic could not be resolved: {error}"
            )
            print(
                "Please enter the topic again."
            )
            continue

        # ----------------------------------------------------
        # 4. READ RESOLUTION STATUS
        # ----------------------------------------------------

        status = getattr(
            topic_result,
            "status",
            "invalid",
        )

        resolved_topic = getattr(
            topic_result,
            "topic",
            raw_topic,
        )

        resolved_subject = getattr(
            topic_result,
            "subject",
            None,
        )

        possible_subjects = getattr(
            topic_result,
            "possible_subjects",
            [],
        )

        reason = getattr(
            topic_result,
            "reason",
            "",
        )

        # ----------------------------------------------------
        # 5. INVALID TOPIC
        # ----------------------------------------------------

        if status == "invalid":

            print()
            print(
                "Invalid topic."
            )

            if reason:
                print(
                    f"Reason: {reason}"
                )

            print(
                "Please enter a valid academic "
                "topic again."
            )

            continue

        # ----------------------------------------------------
        # 6. AMBIGUOUS TOPIC
        # ----------------------------------------------------

        if status == "ambiguous":

            print()
            print(
                f"'{raw_topic}' is ambiguous."
            )

            if possible_subjects:
                print(
                    "Possible subjects:"
                )

                print_numbered_items(
                    possible_subjects
                )

            while True:

                subject = input(
                    "Please specify the subject: "
                ).strip()

                if subject:
                    break

                print(
                    "Subject cannot be empty."
                )

            resolved_subject = subject

            break

        # ----------------------------------------------------
        # 7. VALID TOPIC
        # ----------------------------------------------------

        if status == "valid":

            if not resolved_subject:

                print()
                print(
                    "The topic was marked valid, "
                    "but no subject was returned."
                )

                while True:

                    resolved_subject = input(
                        "Please specify the subject: "
                    ).strip()

                    if resolved_subject:
                        break

                    print(
                        "Subject cannot be empty."
                    )

            break

        # ----------------------------------------------------
        # 8. UNKNOWN STATUS
        # ----------------------------------------------------

        print()
        print(
            "The topic resolver returned an "
            "unexpected result."
        )
        print(
            "Please enter the topic again."
        )

    # --------------------------------------------------------
    # FINAL TOPIC AND SUBJECT
    # --------------------------------------------------------

    topic = resolved_topic or raw_topic
    subject = resolved_subject or ""

    # --------------------------------------------------------
    # 9. DIFFICULTY
    # --------------------------------------------------------

    while True:

        difficulty = input(
            "Difficulty "
            "(basic / standard / advanced): "
        ).strip().lower()

        is_valid_difficulty, difficulty_message = (
            basic_difficulty_check(
                difficulty
            )
        )

        if is_valid_difficulty:
            break

        print()
        print(
            f"Invalid difficulty: "
            f"{difficulty_message}"
        )

    return (
        topic,
        subject,
        academic_level,
        difficulty,
    )


# ============================================================
# MAIN APPLICATION
# ============================================================

def main() -> None:
    """Run the complete Novateach AI pipeline."""

    print_line("=")

    print(
        "WELCOME TO NOVATEACH AI"
    )

    print(
        "Your personalized learning system"
    )

    print_line("=")

    # --------------------------------------------------------
    # 1. DATABASE
    # --------------------------------------------------------

    create_tables()

    # --------------------------------------------------------
    # 2. LOGIN
    # --------------------------------------------------------

    user = login()

    if not user:
        print()
        print(
            "Login failed. "
            "Exiting Novateach AI."
        )
        return

    # --------------------------------------------------------
    # 3. EXTRACT USERNAME AND NAME
    # --------------------------------------------------------

    if isinstance(user, dict):
        username = user.get("username")
        name = user.get("name")
    else:
        username = user
        name = None

    if not username:
        print()
        print(
            "Could not identify "
            "logged-in user."
        )
        return

    # --------------------------------------------------------
    # 4. PROFILE SETUP / LOADING
    # --------------------------------------------------------

    profile = load_profile(
        username
    )

    if not profile:

        if not name:
            print()
            print(
                "Could not load learner name. "
                "Exiting."
            )
            return

        profile = run_onboarding(
            username,
            name,
        )

    if not profile:
        print()
        print(
            "Could not load learner "
            "profile. Exiting."
        )
        return

    # --------------------------------------------------------
    # 5. BUILD CURRENT ADAPTIVE LEARNER CONTEXT
    # --------------------------------------------------------

    # The onboarding profile is only the learner's
    # starting point.
    #
    # The compact learner context combines it with
    # longitudinal evidence from:
    #
    # - quiz performance
    # - concept mastery
    # - recurring error patterns
    # - skill estimates
    # - retest/adaptation decisions
    #
    # This is what allows future lessons to adapt
    # over time instead of relying only on onboarding.

    learner_context = get_compact_learner_context(
        username
    )

    if not learner_context:
        print()
        print(
            "Could not build the adaptive "
            "learner context."
        )
        return

    # --------------------------------------------------------
    # 6. LESSON REQUEST
    # --------------------------------------------------------

    (
        topic,
        subject,
        academic_level,
        difficulty,
    ) = get_lesson_request()

    # --------------------------------------------------------
    # 7. LESSON BLUEPRINT
    # --------------------------------------------------------

    print_heading(
        "Generating personalized "
        "learning blueprint"
    )

    print(
        "Novateach is deciding:"
    )

    print(
        "- what concepts should be taught"
    )

    print(
        "- in what order they should be taught"
    )

    print(
        "- which explanations suit the learner"
    )

    print(
        "- where examples and practice "
        "should appear"
    )

    blueprint = plan_lesson(
        topic=topic,
        subject=subject,
        academic_level=academic_level,
        difficulty=difficulty,
        learner_profile=learner_context,
    )

    if not blueprint:
        print()
        print(
            "Could not generate the "
            "learning blueprint."
        )
        return

    print()
    print(
        "Learning blueprint generated "
        "successfully."
    )

    # --------------------------------------------------------
    # 8. TEXTBOOK LESSON GENERATION
    # --------------------------------------------------------

    print_heading(
        "Producing textbook lesson"
    )

    print(
        "Novateach is converting "
        "the blueprint into:"
    )

    print(
        "- readable explanations"
    )

    print(
        "- formulas and symbol meanings"
    )

    print(
        "- derivations where useful"
    )

    print(
        "- solved examples"
    )

    print(
        "- misconceptions"
    )

    print(
        "- visual requirements"
    )

    print(
        "- practice questions"
    )

    textbook_lesson = (
        generate_lecture_production_plan(
            blueprint
        )
    )

    if not textbook_lesson:
        print()
        print(
            "Could not generate the "
            "textbook lesson."
        )
        return

    # --------------------------------------------------------
    # 9. DISPLAY TEXTBOOK
    # --------------------------------------------------------

    print_textbook_lesson(
        textbook_lesson
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()