import re

from ai_generator import generate_with_ai

from modeles.input_resolution import (
    TopicResolution,
    LearningSignalResult,
)


# ============================================================
# BASIC TOPIC CHECK
# ============================================================

def basic_topic_check(topic):
    """
    Perform cheap deterministic validation before using AI.
    """

    if topic is None:
        return False, "Topic cannot be empty."

    topic = topic.strip()

    if not topic:
        return False, "Topic cannot be empty."

    if len(topic) < 2:
        return False, "Topic is too short."

    if len(topic) > 200:
        return False, "Topic is too long."

    return True, None


# ============================================================
# ACADEMIC LEVEL CHECK
# ============================================================

def basic_academic_level_check(academic_level):
    """
    Validate the academic level before sending it to AI.

    Accepted examples:
        10
        10th
        Grade 10
        Class 10
        12th grade
        undergraduate
        college
        A-level
    """

    if academic_level is None:
        return False, "Academic level cannot be empty."

    academic_level = academic_level.strip()

    if not academic_level:
        return False, "Academic level cannot be empty."

    if len(academic_level) > 100:
        return False, "Academic level is too long."

    normalized = academic_level.lower()

    # --------------------------------------------------------
    # PLAIN NUMERIC SCHOOL LEVEL
    # --------------------------------------------------------

    if re.fullmatch(r"(?:[1-9]|1[0-2])", normalized):
        return True, None

    # --------------------------------------------------------
    # COMMON SCHOOL / COLLEGE LEVEL FORMATS
    # --------------------------------------------------------

    valid_patterns = [
        # Grade 10 / grade 10
        r"\bgrade\s*(?:[1-9]|1[0-2])\b",

        # Class 10 / class 12
        r"\bclass\s*(?:[1-9]|1[0-2])\b",

        # Standard 10 / standard 12
        r"\bstandard\s*(?:[1-9]|1[0-2])\b",

        # 10th grade / 10th class / 10th standard
        r"\b(?:[1-9]|1[0-2])(?:st|nd|rd|th)\s*"
        r"(?:grade|class|standard)\b",

        # 10th / 11th / 12th
        r"\b(?:[1-9]|1[0-2])(?:st|nd|rd|th)\b",

        # School levels
        r"\bprimary\s*school\b",
        r"\belementary\s*school\b",
        r"\bmiddle\s*school\b",
        r"\bsecondary\s*school\b",
        r"\bhigh\s*school\b",
        r"\bjunior\s*high\s*school\b",
        r"\bsenior\s*high\s*school\b",

        # Higher education
        r"\bundergraduate\b",
        r"\bpostgraduate\b",
        r"\bgraduate\b",
        r"\bcollege\b",
        r"\buniversity\b",

        # College year terminology
        r"\bfreshman\b",
        r"\bsophomore\b",
        r"\bjunior\b",
        r"\bsenior\b",

        # Degrees
        r"\bbachelor\b",
        r"\bmaster\b",
        r"\bphd\b",
        r"\bdoctorate\b",

        # International systems
        r"\bib\b",
        r"\ba[- ]level\b",
        r"\bas[- ]level\b",
        r"\bgcse\b",
        r"\bigcse\b",
    ]

    for pattern in valid_patterns:
        if re.search(pattern, normalized):
            return True, None

    return (
        False,
        "Academic level is not recognized. "
        "Please enter something like '10', 'Grade 10', "
        "'Class 12', 'A-level', or 'undergraduate'."
    )


# ============================================================
# DIFFICULTY CHECK
# ============================================================

def basic_difficulty_check(difficulty):
    """
    Validate the difficulty level before sending it
    to the Lesson Planner.
    """

    if difficulty is None:
        return False, "Difficulty cannot be empty."

    difficulty = difficulty.strip().lower()

    allowed_difficulties = {
        "basic",
        "standard",
        "advanced",
    }

    if difficulty not in allowed_difficulties:
        return (
            False,
            "Difficulty must be basic, standard, or advanced."
        )

    return True, None


# ============================================================
# TOPIC RESOLUTION PROMPT
# ============================================================

def build_topic_resolution_prompt(topic, academic_level):
    return f"""
You are the Topic Resolution and Semantic Classification
system for Novateach.

Your job has TWO responsibilities:

1. Determine whether the student's requested learning topic
   is usable and identify its academic subject.

2. Build a semantic topic profile that tells downstream
   Novateach systems WHAT KIND OF CONTENT this topic genuinely
   requires.

The semantic profile is extremely important.

It will later control:
- lesson planning
- textbook structure
- examples
- practice questions
- formula generation
- numerical problem generation
- visual requirements

Do NOT classify a topic based only on its subject.

For example:

Physics does NOT automatically mean formulas.

Psychology does NOT automatically mean no quantitative
content.

The actual topic determines the content requirements.

==================================================
STUDENT INPUT
==================================================

Student topic:
{topic}

Academic level:
{academic_level}

==================================================
STEP 1 — TOPIC STATUS
==================================================

Classify the input into EXACTLY one of:

1. valid
2. ambiguous
3. invalid

==================================================
VALID
==================================================

Use "valid" when the topic represents a meaningful educational
topic and its subject can reasonably be identified.

Example:

"Newton's laws"

→ valid
→ Physics

==================================================
AMBIGUOUS
==================================================

Use "ambiguous" when the topic is meaningful but could refer
to substantially different subjects or concepts.

Example:

"Vectors"

Possible subjects:

- Mathematics
- Physics

Do NOT randomly choose one.

For an ambiguous topic:
- provide possible_subjects
- do not invent a semantic profile that depends on choosing
  one subject

==================================================
INVALID
==================================================

Use "invalid" when the input is meaningless, random,
not a recognizable educational topic, or otherwise cannot
reasonably be interpreted as a learning topic.

Do not invent a topic from meaningless text.

==================================================
STEP 2 — SEMANTIC TOPIC PROFILE
==================================================

For a VALID topic, determine the following:

--------------------------------------------------
DOMAIN
--------------------------------------------------

"domain" describes the broad knowledge domain.

Examples:

- physical_science
- mathematical_science
- behavioural_science
- social_science
- humanities
- history
- language
- computer_science
- engineering
- life_science
- practical_skills
- mixed

Use the most appropriate domain.

--------------------------------------------------
TOPIC TYPE
--------------------------------------------------

"topic_type" describes the nature of the requested topic.

Possible values include:

- conceptual
- mathematical
- scientific
- social_behavioural
- historical
- linguistic
- programming
- practical_procedural
- mixed

Choose the type that best represents the actual topic.

--------------------------------------------------
CONTENT MODES
--------------------------------------------------

"content_modes" is a list of the teaching approaches that
genuinely fit the topic.

Possible values include:

- concepts
- definitions
- theories
- mechanisms
- examples
- scenarios
- case_studies
- comparisons
- patterns
- principles
- equations
- derivations
- numerical_problems
- applications
- diagrams
- processes
- code
- procedures
- experiments
- source_analysis

Do NOT include a mode merely because it sounds academic.

Only include modes genuinely useful for this topic.

--------------------------------------------------
FORMULA RELEVANCE
--------------------------------------------------

"formula_relevant" answers:

Are genuine mathematical formulas, equations, or quantitative
relationships an important part of understanding this specific
topic?

Return:

true
or
false

Do NOT use the subject alone to decide this.

--------------------------------------------------
QUANTITATIVE RELEVANCE
--------------------------------------------------

"quantitative_relevant" answers:

Does understanding this topic meaningfully require numerical
quantities, calculations, measurement, statistical reasoning,
or quantitative analysis?

Return:

true
or
false

Again, classify the actual topic, not merely the subject.

==================================================
IMPORTANT SEMANTIC RULE
==================================================

The semantic profile must describe the TOPIC itself.

For example:

Topic:
"Human Behaviour"

Possible classification:

domain:
behavioural_science

topic_type:
social_behavioural

content_modes:
[
    "concepts",
    "definitions",
    "theories",
    "mechanisms",
    "examples",
    "scenarios",
    "comparisons",
    "case_studies"
]

formula_relevant:
false

quantitative_relevant:
false

Do NOT invent equations or numerical problems simply because
the lesson should look academically sophisticated.

Another example:

Topic:
"Electric Field"

Possible classification:

domain:
physical_science

topic_type:
scientific

content_modes:
[
    "concepts",
    "definitions",
    "principles",
    "equations",
    "applications",
    "diagrams",
    "numerical_problems"
]

formula_relevant:
true

quantitative_relevant:
true

These are examples of the reasoning expected.
Do not blindly copy them for unrelated topics.

==================================================
SEMANTIC CONSISTENCY
==================================================

The following relationships must hold:

If formula_relevant is false:
- "equations" should normally NOT appear in content_modes.
- "derivations" should normally NOT appear in content_modes.
- "numerical_problems" should normally NOT appear unless there
  is a genuine non-formula quantitative reason.

If quantitative_relevant is false:
- "numerical_problems" should normally NOT appear.

If the topic is conceptual or social/behavioural:
- prioritize concepts, theories, mechanisms, examples,
  scenarios, comparisons, and case studies where relevant.

If the topic genuinely requires mathematics:
- equations, derivations, and numerical problems may be included.

Do not force either direction.

==================================================
AMBIGUOUS / INVALID TOPICS
==================================================

If status is "ambiguous" or "invalid":

- domain may be null
- topic_type may be null
- content_modes should be []
- formula_relevant should be null
- quantitative_relevant should be null

Do not guess semantic information when the topic itself
cannot yet be reliably resolved.

==================================================
RETURN ONLY VALID JSON
==================================================

Return exactly this structure:

{{
    "status": "valid | ambiguous | invalid",
    "topic": "",
    "subject": null,
    "possible_subjects": [],
    "reason": "",
    "domain": null,
    "topic_type": null,
    "content_modes": [],
    "formula_relevant": null,
    "quantitative_relevant": null
}}
"""


# ============================================================
# RESOLVE TOPIC
# ============================================================

def resolve_topic(topic, academic_level):
    """
    Validate and resolve a topic using AI.

    The resolver now returns both:
    - basic topic resolution
    - semantic topic classification
    """

    if topic is None:
        topic = ""

    if academic_level is None:
        academic_level = ""

    topic = topic.strip()
    academic_level = academic_level.strip()

    # --------------------------------------------------------
    # BASIC TOPIC VALIDATION
    # --------------------------------------------------------

    is_valid, reason = basic_topic_check(topic)

    if not is_valid:
        return TopicResolution(
            status="invalid",
            topic=topic,
            reason=reason,
        )

    # --------------------------------------------------------
    # BASIC ACADEMIC LEVEL VALIDATION
    # --------------------------------------------------------

    is_valid, reason = basic_academic_level_check(
        academic_level
    )

    if not is_valid:
        raise ValueError(reason)

    # --------------------------------------------------------
    # AI TOPIC RESOLUTION
    # --------------------------------------------------------

    prompt = build_topic_resolution_prompt(
        topic,
        academic_level,
    )

    result = generate_with_ai(
        prompt,
        expect_json=True,
    )

    if not isinstance(result, dict):
        raise ValueError(
            "Topic Resolver received invalid AI output."
        )

    # --------------------------------------------------------
    # STATUS VALIDATION
    # --------------------------------------------------------

    status = result.get("status")

    if status not in {
        "valid",
        "ambiguous",
        "invalid",
    }:
        raise ValueError(
            f"Topic Resolver returned unknown status: {status}"
        )

    # --------------------------------------------------------
    # FIELD VALIDATION
    # --------------------------------------------------------

    resolved_topic = result.get("topic")

    if resolved_topic is not None and not isinstance(
        resolved_topic,
        str,
    ):
        raise ValueError(
            "Topic Resolver 'topic' must be a string."
        )

    subject = result.get("subject")

    if subject is not None and not isinstance(
        subject,
        str,
    ):
        raise ValueError(
            "Topic Resolver 'subject' must be a string or null."
        )

    possible_subjects = result.get(
        "possible_subjects",
        [],
    )

    if not isinstance(possible_subjects, list):
        raise ValueError(
            "Topic Resolver 'possible_subjects' "
            "must be a list."
        )

    cleaned_possible_subjects = []

    for possible_subject in possible_subjects:
        if not isinstance(possible_subject, str):
            continue

        possible_subject = possible_subject.strip()

        if possible_subject:
            cleaned_possible_subjects.append(
                possible_subject
            )

    reason = result.get("reason")

    if reason is not None and not isinstance(
        reason,
        str,
    ):
        raise ValueError(
            "Topic Resolver 'reason' must be a string or null."
        )

    # --------------------------------------------------------
    # SEMANTIC PROFILE VALIDATION
    # --------------------------------------------------------

    domain = result.get("domain")
    topic_type = result.get("topic_type")
    content_modes = result.get(
        "content_modes",
        [],
    )
    formula_relevant = result.get("formula_relevant")
    quantitative_relevant = result.get(
        "quantitative_relevant"
    )

    # --------------------------------------------------------
    # DOMAIN
    # --------------------------------------------------------

    if domain is not None and not isinstance(
        domain,
        str,
    ):
        raise ValueError(
            "Topic Resolver 'domain' must be a string or null."
        )

    if isinstance(domain, str):
        domain = domain.strip() or None

    # --------------------------------------------------------
    # TOPIC TYPE
    # --------------------------------------------------------

    if topic_type is not None and not isinstance(
        topic_type,
        str,
    ):
        raise ValueError(
            "Topic Resolver 'topic_type' "
            "must be a string or null."
        )

    if isinstance(topic_type, str):
        topic_type = topic_type.strip() or None

    # --------------------------------------------------------
    # CONTENT MODES
    # --------------------------------------------------------

    if not isinstance(content_modes, list):
        raise ValueError(
            "Topic Resolver 'content_modes' must be a list."
        )

    cleaned_content_modes = []

    for content_mode in content_modes:
        if not isinstance(content_mode, str):
            continue

        content_mode = content_mode.strip()

        if content_mode:
            cleaned_content_modes.append(
                content_mode
            )

    # --------------------------------------------------------
    # BOOLEAN SEMANTIC FIELDS
    # --------------------------------------------------------

    if formula_relevant is not None and not isinstance(
        formula_relevant,
        bool,
    ):
        raise ValueError(
            "Topic Resolver 'formula_relevant' "
            "must be true, false, or null."
        )

    if quantitative_relevant is not None and not isinstance(
        quantitative_relevant,
        bool,
    ):
        raise ValueError(
            "Topic Resolver 'quantitative_relevant' "
            "must be true, false, or null."
        )

    # --------------------------------------------------------
    # VALID TOPIC REQUIREMENTS
    # --------------------------------------------------------

    if status == "valid":
        if not subject:
            raise ValueError(
                "Topic Resolver marked the topic as valid "
                "but did not provide a subject."
            )

        if not domain:
            raise ValueError(
                "Topic Resolver marked the topic as valid "
                "but did not provide a domain."
            )

        if not topic_type:
            raise ValueError(
                "Topic Resolver marked the topic as valid "
                "but did not provide a topic_type."
            )

        if not cleaned_content_modes:
            raise ValueError(
                "Topic Resolver marked the topic as valid "
                "but provided no content_modes."
            )

        if formula_relevant is None:
            raise ValueError(
                "Topic Resolver marked the topic as valid "
                "but did not provide formula_relevant."
            )

        if quantitative_relevant is None:
            raise ValueError(
                "Topic Resolver marked the topic as valid "
                "but did not provide quantitative_relevant."
            )

    # --------------------------------------------------------
    # AMBIGUOUS TOPIC REQUIREMENTS
    # --------------------------------------------------------

    if (
        status == "ambiguous"
        and not cleaned_possible_subjects
    ):
        raise ValueError(
            "Topic Resolver marked the topic as ambiguous "
            "but provided no possible subjects."
        )

    # --------------------------------------------------------
    # INVALID TOPIC NORMALIZATION
    # --------------------------------------------------------

    if status == "invalid":
        subject = None
        cleaned_possible_subjects = []

        domain = None
        topic_type = None
        cleaned_content_modes = []

        formula_relevant = None
        quantitative_relevant = None

    # --------------------------------------------------------
    # AMBIGUOUS TOPIC NORMALIZATION
    # --------------------------------------------------------

    if status == "ambiguous":
        domain = None
        topic_type = None
        cleaned_content_modes = []

        formula_relevant = None
        quantitative_relevant = None

    # --------------------------------------------------------
    # RETURN RESOLUTION
    # --------------------------------------------------------

    return TopicResolution(
        status=status,
        topic=resolved_topic or topic,
        subject=subject,
        possible_subjects=cleaned_possible_subjects,
        reason=reason,
        domain=domain,
        topic_type=topic_type,
        content_modes=cleaned_content_modes,
        formula_relevant=formula_relevant,
        quantitative_relevant=quantitative_relevant,
    )


# ============================================================
# Q7 LEARNING SIGNAL EXTRACTION PROMPT
# ============================================================

def build_learning_signal_prompt(extra_info):
    return f"""
You are the learner-signal extraction system for Novateach.

The student provided optional free-form information about
how they learn.

Your job is to extract ONLY information that can genuinely
help Novateach teach this student better.

Student text:

{extra_info}

Rules:

1. Ignore irrelevant personal information.
2. Ignore jokes and casual conversation.
3. Do not invent preferences.
4. Do not diagnose personality or learning disorders.
5. Do not treat random facts as learning preferences.
6. Preserve useful learning preferences.
7. Keep each signal concise and actionable.
8. If nothing useful exists, return an empty list.

Useful signals may describe things such as:

- preferred explanation style
- preferred examples
- preferred pacing
- difficulty with long explanations
- need for practice
- need for visual explanations
- need for step-by-step explanations
- useful revision patterns

Return ONLY valid JSON:

{{
    "relevant": true,
    "learning_signals": []
}}
"""


# ============================================================
# Q7 LEARNING SIGNAL EXTRACTION
# ============================================================

def extract_learning_signals(extra_info):
    """
    Extract useful learning preferences from optional Q7 text.
    """

    if extra_info is None or not extra_info.strip():
        return LearningSignalResult(
            relevant=False,
            learning_signals=[],
        )

    extra_info = extra_info.strip()

    # --------------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------------

    if len(extra_info) > 1000:
        raise ValueError(
            "Q7 response is too long. "
            "Please keep it under 1000 characters."
        )

    prompt = build_learning_signal_prompt(
        extra_info
    )

    result = generate_with_ai(
        prompt,
        expect_json=True,
    )

    if not isinstance(result, dict):
        raise ValueError(
            "Learning Signal Extractor received "
            "invalid AI output."
        )

    # --------------------------------------------------------
    # SCHEMA VALIDATION
    # --------------------------------------------------------

    if "relevant" not in result:
        raise ValueError(
            "Learning Signal Extractor response "
            "is missing 'relevant'."
        )

    if "learning_signals" not in result:
        raise ValueError(
            "Learning Signal Extractor response "
            "is missing 'learning_signals'."
        )

    if not isinstance(
        result["relevant"],
        bool,
    ):
        raise ValueError(
            "'relevant' must be a boolean."
        )

    signals = result["learning_signals"]

    if not isinstance(signals, list):
        raise ValueError(
            "'learning_signals' must be a list."
        )

    # --------------------------------------------------------
    # CLEAN SIGNALS
    # --------------------------------------------------------

    cleaned_signals = []

    for signal in signals:
        if not isinstance(signal, str):
            continue

        signal = signal.strip()

        if not signal:
            continue

        if len(signal) > 200:
            continue

        cleaned_signals.append(signal)

    # --------------------------------------------------------
    # LIMIT OUTPUT
    # --------------------------------------------------------

    cleaned_signals = cleaned_signals[:5]

    # --------------------------------------------------------
    # CONSISTENCY VALIDATION
    # --------------------------------------------------------

    if not result["relevant"]:
        cleaned_signals = []

    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return LearningSignalResult(
        relevant=result["relevant"],
        learning_signals=cleaned_signals,
    )