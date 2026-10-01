import json
import re
from typing import Any

from ai_generator import generate_with_ai

from services.knowledge_graph_service import (
    get_graph_by_key,
    save_knowledge_graph,
)


GRAPH_SCHEMA = {
    "concepts": [
        {
            "concept_key": "example_concept",
            "name": "Example Concept",
            "description": "Short explanation of the concept.",
            "concept_type": "general",
            "importance": 0.8,
            "metadata": {},
        }
    ],
    "relationships": [
        {
            "from_concept": "prerequisite_concept",
            "to_concept": "target_concept",
            "relationship_type": "prerequisite",
            "confidence": 0.95,
        }
    ],
}


def _extract_json(text: str) -> dict[str, Any]:
    """
    Extract a JSON object from an AI response.
    """

    if not isinstance(text, str):
        raise ValueError(
            "AI graph response must be a string or dictionary."
        )

    text = text.strip()

    try:
        result = json.loads(text)

        if not isinstance(result, dict):
            raise ValueError(
                "AI response must be a JSON object."
            )

        return result

    except json.JSONDecodeError:
        pass

    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL,
    )

    if not match:
        raise ValueError(
            "AI response did not contain valid JSON."
        )

    try:
        result = json.loads(match.group(0))
    except json.JSONDecodeError as error:
        raise ValueError(
            "AI response contained invalid JSON."
        ) from error

    if not isinstance(result, dict):
        raise ValueError(
            "Extracted graph must be a JSON object."
        )

    return result


def _build_graph_prompt(
    topic: str,
    subject: str,
    academic_level: str,
) -> str:
    """
    Create the prompt used to generate a knowledge graph.
    """

    return f"""
You are generating a prerequisite knowledge graph for an
Explainable Intelligent Tutoring System.

Topic:
{topic}

Subject:
{subject}

Academic level:
{academic_level}

Build a compact but meaningful learning graph.

Requirements:

1. Include the central topic.
2. Include important prerequisite concepts.
3. Include concepts that naturally follow from the topic.
4. Use prerequisite relationships when one concept is
   required to understand another.
5. Do not invent unnecessary concepts.
6. Keep the graph suitable for an educational tutoring system.
7. The graph must be a directed acyclic graph.
8. Do not create circular prerequisites.
9. Use stable snake_case concept_key values.
10. Return ONLY valid JSON.

Required JSON structure:

{json.dumps(GRAPH_SCHEMA, indent=2)}

Relationship semantics:

"prerequisite":
    from_concept must be understood before to_concept.

"depends_on":
    from_concept is a dependency of to_concept.

"related":
    concepts are related but neither is necessarily
    a prerequisite.

"part_of":
    from_concept is a component of to_concept.

Return only the JSON object.
"""


def generate_knowledge_graph(
    *,
    topic: str,
    subject: str,
    academic_level: str,
    graph_key: str | None = None,
) -> int:
    """
    Generate, validate, and save a knowledge graph.

    If a graph with the same graph key already exists,
    return the existing graph ID instead of generating
    a duplicate.

    Returns:
        graph_id
    """

    topic = topic.strip()
    subject = subject.strip()
    academic_level = academic_level.strip()

    if not topic:
        raise ValueError("topic cannot be empty.")

    if not subject:
        raise ValueError("subject cannot be empty.")

    if not academic_level:
        raise ValueError(
            "academic_level cannot be empty."
        )

    if graph_key is None:
        graph_key = _make_graph_key(
            topic=topic,
            subject=subject,
            academic_level=academic_level,
        )
    else:
        graph_key = graph_key.strip()

    if not graph_key:
        raise ValueError("graph_key cannot be empty.")

    existing_graph = get_graph_by_key(graph_key)

    if existing_graph is not None:
        return int(existing_graph["id"])

    prompt = _build_graph_prompt(
        topic=topic,
        subject=subject,
        academic_level=academic_level,
    )

    response = generate_with_ai(
        prompt,
        expect_json=True,
    )

    if isinstance(response, dict):
        graph_data = response
    else:
        graph_data = _extract_json(response)

    try:
        return save_knowledge_graph(
            graph_key=graph_key,
            topic=topic,
            subject=subject,
            academic_level=academic_level,
            graph_data=graph_data,
            version=1,
        )
    except ValueError as error:
        raise ValueError(
            f"Generated knowledge graph was invalid: {error}"
        ) from error


def _make_graph_key(
    *,
    topic: str,
    subject: str,
    academic_level: str,
) -> str:
    """
    Create a normalized and stable database key.
    """

    parts = [
        subject.strip().lower(),
        topic.strip().lower(),
        academic_level.strip().lower(),
    ]

    raw = "_".join(parts)

    key = re.sub(
        r"[^a-z0-9]+",
        "_",
        raw,
    )

    key = re.sub(
        r"_+",
        "_",
        key,
    )

    return key.strip("_")