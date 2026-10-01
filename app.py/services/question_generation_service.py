import json

from typing import Any, Optional

from ai_generator import generate_with_ai

from services.learner_context_service import (
    get_compact_learner_context,
)

from services.question_service import (
    save_question,
    get_questions_for_graph,
)

from services.knowledge_graph_service import (
    get_knowledge_graph,
)


def clean_json_response(response: Any) -> dict[str, Any]:
    """
    Converts the AI response into a Python dictionary.

    Handles:
    - dictionary responses
    - JSON strings
    - markdown JSON code fences
    """

    if isinstance(response, dict):
        return response

    if not isinstance(response, str):
        raise ValueError(
            "AI response must be a dictionary or string"
        )

    cleaned = response.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    try:
        parsed = json.loads(cleaned)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"AI returned invalid JSON: {error}"
        ) from error

    if not isinstance(parsed, dict):
        raise ValueError(
            "AI JSON response must be an object"
        )

    return parsed


def build_question_prompt(
    concept: dict[str, Any],
    topic: str,
    subject: str,
    academic_level: str,
    difficulty: str,
    cognitive_skill: str,
    learner_summary: Optional[dict[str, Any]] = None,
) -> str:
    """
    Builds a domain-aware and learner-aware question generation prompt.
    """

    learner_summary = learner_summary or {}

    return f"""
You are the question-generation engine of Novateach AI.

Generate exactly ONE high-quality educational question.

Topic:
{topic}

Subject:
{subject}

Academic level:
{academic_level}

Target concept:
{concept.get("name")}

Concept description:
{concept.get("description", "")}

Concept type:
{concept.get("concept_type", "general")}

Difficulty:
{difficulty}

Cognitive skill:
{cognitive_skill}

Learner context:
{json.dumps(learner_summary, indent=2, default=str)}

Rules:

1. The question must test the target concept.
2. Do not test an unrelated concept.
3. Match the academic level.
4. Match the requested difficulty.
5. Use the requested cognitive skill.
6. Do not force formulas if the concept is non-mathematical.
7. Do not force an application question if application is unsuitable.
8. Provide a correct answer.
9. Provide a clear explanation.
10. Include possible error types only when meaningful.
11. Use the learner context to make the question appropriately useful.
12. Do not make the question unnecessarily easy or difficult.
13. Return JSON only.
14. Do not add markdown or extra text.

Return exactly this structure:

{{
    "question_key": "unique_string",
    "question_text": "Question shown to the learner",
    "question_type": "mcq",
    "cognitive_skill": "{cognitive_skill}",
    "difficulty": "{difficulty}",
    "answer_format": "text",
    "expected_answer": "Correct answer",
    "explanation": "Clear explanation",
    "possible_error_types": [],
    "prerequisite_concepts": [],
    "metadata": {{
        "topic": "{topic}",
        "subject": "{subject}"
    }}
}}
"""


def generate_question(
    graph_id: int,
    concept_id: int,
    topic: str,
    subject: str,
    academic_level: str,
    difficulty: str = "standard",
    cognitive_skill: str = "conceptual_understanding",
    learner_summary: Optional[dict[str, Any]] = None,
    username: Optional[str] = None,
) -> dict[str, Any]:
    """
    Generates, validates, saves, and returns one AI question.

    Learner context behavior:

    1. If learner_summary is provided, use it.
    2. If learner_summary is not provided but username is provided,
       automatically load the learner's compact context.
    3. If neither is provided, generate a general question.
    """

    graph = get_knowledge_graph(graph_id)

    if graph is None:
        raise ValueError(
            f"No knowledge graph found with ID: {graph_id}"
        )

    concept = None

    for item in graph["concepts"]:
        if item["id"] == concept_id:
            concept = item
            break

    if concept is None:
        raise ValueError(
            f"Concept {concept_id} does not belong to graph {graph_id}"
        )

    # Automatically load learner context when username is provided.
    if learner_summary is None and username is not None:
        learner_summary = get_compact_learner_context(username)

    prompt = build_question_prompt(
        concept=concept,
        topic=topic,
        subject=subject,
        academic_level=academic_level,
        difficulty=difficulty,
        cognitive_skill=cognitive_skill,
        learner_summary=learner_summary,
    )

    ai_response = generate_with_ai(
        prompt,
        expect_json=True,
    )

    question_data = clean_json_response(ai_response)

    # Ensure the requested values cannot be silently changed by AI.
    question_data["cognitive_skill"] = cognitive_skill
    question_data["difficulty"] = difficulty

    question_id = save_question(
        question_data=question_data,
        graph_id=graph_id,
        concept_id=concept_id,
        generation_source="ai",
    )

    saved_question = {
        "id": question_id,
        "graph_id": graph_id,
        "concept_id": concept_id,
        **question_data,
    }

    return saved_question


def generate_questions_for_concept(
    graph_id: int,
    concept_id: int,
    topic: str,
    subject: str,
    academic_level: str,
    count: int = 5,
    difficulty: str = "standard",
    cognitive_skill: str = "conceptual_understanding",
    learner_summary: Optional[dict[str, Any]] = None,
    username: Optional[str] = None,
) -> list[dict[str, Any]]:
    """
    Generates multiple questions for one concept.

    Existing questions are returned if generation is not needed.

    Learner context can be provided directly through learner_summary
    or automatically loaded through username.
    """

    if count < 1:
        raise ValueError(
            "count must be at least 1"
        )

    existing_questions = get_questions_for_graph(
        graph_id=graph_id,
        concept_id=concept_id,
        difficulty=difficulty,
        cognitive_skill=cognitive_skill,
        limit=count,
    )

    questions = list(existing_questions)

    remaining = count - len(questions)

    for _ in range(remaining):
        question = generate_question(
            graph_id=graph_id,
            concept_id=concept_id,
            topic=topic,
            subject=subject,
            academic_level=academic_level,
            difficulty=difficulty,
            cognitive_skill=cognitive_skill,
            learner_summary=learner_summary,
            username=username,
        )

        questions.append(question)

    return questions