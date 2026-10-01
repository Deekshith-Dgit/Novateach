from __future__ import annotations

import json
from typing import Any

from ai_generator import generate_with_ai
from modeles.lecture_session import ContentNode


def normalize_string(value: Any) -> str:
    if not isinstance(value, str):
        return ""

    return value.strip()


def normalize_status(
    value: Any,
    default: str = "upcoming",
) -> str:
    allowed = {
        "recommended",
        "current",
        "ready",
        "upcoming",
        "locked",
        "completed",
    }

    if isinstance(value, str):
        value = value.strip().lower()

        if value in allowed:
            return value

    return default


def normalize_page_count(
    difficulty: str,
) -> int:
    difficulty = difficulty.strip().lower()

    if difficulty == "basic":
        return 5

    if difficulty == "advanced":
        return 8

    return 6




def build_topic_plan_prompt(
    topic: str,
    academic_level: str,
    difficulty: str,
    learner_profile: dict[str, Any] | None = None,
) -> str:
    page_count = normalize_page_count(difficulty)

    return f"""
You are designing a personalized learning path for Novateach.

The learner wants to study:

Topic: {topic}
Academic level: {academic_level}
Difficulty: {difficulty}
Learner profile: {learner_profile or {}}

Create a prerequisite-aware table of contents for this topic.

This must work for ANY educational domain:
- mathematics
- physics
- biology
- chemistry
- psychology
- history
- economics
- programming
- languages
- literature
- or any other valid subject

Do not assume the topic is mathematics.
Do not invent formulas unless the topic genuinely needs them.

============================================================
PREREQUISITE RULES
============================================================

Identify only the prerequisites genuinely needed to begin
the requested topic.

Use the learner's academic level as an initial estimate of
what they may know, but do not assume mastery of the current
academic level.

Prerequisites must be:
- foundational
- directly relevant
- teachable as short learning units
- understandable as independent concepts

Use no more than 3 prerequisites.

The most important prerequisite must be numbered -1.
Earlier prerequisites may be numbered -2 or -3.

============================================================
MAIN TOPIC RULES
============================================================

Create approximately {page_count} main learning pages.

The main pages must:
- progress from simpler to deeper ideas
- match the selected difficulty
- avoid repeating the same concept
- include a logical learning objective
- lead naturally toward a final quiz

Do not generate full lesson content.
Generate only the learning roadmap.

============================================================
OUTPUT FORMAT
============================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
  "topic": "{topic}",
  "academic_level": "{academic_level}",
  "difficulty": "{difficulty}",
  "prerequisites": [
    {{
      "node_id": "stable_snake_case_id",
      "title": "Prerequisite title",
      "objective": "What the learner should understand",
      "reason": "Why this prerequisite is needed",
      "estimated_minutes": 8,
      "status": "recommended"
    }}
  ],
  "main_pages": [
    {{
      "node_id": "stable_snake_case_id",
      "title": "Page title",
      "objective": "What the learner should understand",
      "estimated_minutes": 10,
      "status": "current"
    }}
  ]
}}

Requirements:
- Return valid JSON only.
- Do not use Markdown.
- Do not include explanations outside JSON.
- Do not create empty titles.
- Do not duplicate concepts.
- Do not create generic pages such as "Introduction" unless
  the introduction has a specific learning objective.
"""




def clean_ai_json(
    raw_result: Any,
) -> dict[str, Any]:
    """
    Convert the AI topic-plan response into a dictionary.

    The AI helper may return:
    - a Python dictionary
    - a JSON string
    - a JSON string wrapped in Markdown fences
    """

    if isinstance(raw_result, dict):
        return raw_result

    if not isinstance(raw_result, str):
        raise ValueError(
            "Topic plan AI output must be a dictionary "
            "or a JSON string."
        )

    text = raw_result.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```JSON", "")
        text = text.replace("```", "")
        text = text.strip()

    try:
        data = json.loads(text)

    except json.JSONDecodeError as error:
        raise ValueError(
            "Topic planner returned invalid JSON."
        ) from error

    if not isinstance(data, dict):
        raise ValueError(
            "Topic planner JSON must be an object."
        )

    return data




def build_prerequisite_nodes(
    raw_items: Any,
) -> list[ContentNode]:
    if not isinstance(raw_items, list):
        return []

    cleaned_items = []

    for item in raw_items:
        if not isinstance(item, dict):
            continue

        title = normalize_string(
            item.get("title")
        )

        objective = normalize_string(
            item.get("objective")
        )

        node_id = normalize_string(
            item.get("node_id")
        )

        reason = normalize_string(
            item.get("reason")
        )

        if not title or not objective:
            continue

        if not node_id:
            node_id = (
                title.lower()
                .replace(" ", "_")
                .replace("-", "_")
            )

        cleaned_items.append(
            {
                "node_id": node_id,
                "title": title,
                "objective": objective,
                "reason": reason,
                "estimated_minutes": item.get(
                    "estimated_minutes",
                    8,
                ),
                "status": normalize_status(
                    item.get("status"),
                    "recommended",
                ),
            }
        )

    cleaned_items = cleaned_items[:3]

    total = len(cleaned_items)
    nodes = []

    for index, item in enumerate(cleaned_items):
        display_number = index - total

        nodes.append(
            ContentNode(
                node_id=item["node_id"],
                title=item["title"],
                display_number=display_number,
                node_type="prerequisite",
                objective=item["objective"],
                status=item["status"],
                reason=item["reason"],
                estimated_minutes=int(
                    item["estimated_minutes"]
                ),
            )
        )

    return nodes  




def build_main_page_nodes(
    raw_items: Any,
) -> list[ContentNode]:
    if not isinstance(raw_items, list):
        return []

    nodes = []

    for index, item in enumerate(raw_items):
        if not isinstance(item, dict):
            continue

        title = normalize_string(
            item.get("title")
        )

        objective = normalize_string(
            item.get("objective")
        )

        node_id = normalize_string(
            item.get("node_id")
        )

        if not title or not objective:
            continue

        if not node_id:
            node_id = (
                title.lower()
                .replace(" ", "_")
                .replace("-", "_")
            )

        status = "upcoming"

        if index == 0:
            status = "current"
        elif index == 1:
            status = "ready"

        nodes.append(
            ContentNode(
                node_id=node_id,
                title=title,
                display_number=index + 1,
                node_type="main",
                objective=objective,
                status=status,
                estimated_minutes=int(
                    item.get(
                        "estimated_minutes",
                        8,
                    )
                ),
            )
        )

    return nodes



def validate_topic_plan(
    prerequisites: list[ContentNode],
    main_pages: list[ContentNode],
) -> None:
    if len(prerequisites) > 3:
        raise ValueError(
            "Topic plan cannot contain more than "
            "3 prerequisites."
        )

    if not main_pages:
        raise ValueError(
            "Topic plan must contain at least "
            "one main page."
        )

    seen_ids: set[str] = set()

    for node in prerequisites + main_pages:
        if node.node_id in seen_ids:
            raise ValueError(
                f"Duplicate topic node: {node.node_id}"
            )

        seen_ids.add(node.node_id)

    expected_numbers = list(
        range(
            -len(prerequisites),
            0,
        )
    )

    actual_numbers = [
        node.display_number
        for node in prerequisites
    ]

    if actual_numbers != expected_numbers:
        raise ValueError(
            "Prerequisite numbering is invalid."
        )

    main_numbers = [
        node.display_number
        for node in main_pages
    ]

    expected_main_numbers = list(
        range(
            1,
            len(main_pages) + 1,
        )
    )

    if main_numbers != expected_main_numbers:
        raise ValueError(
            "Main page numbering is invalid."
        )
def build_topic_plan(
    topic: str,
    academic_level: str,
    difficulty: str,
    learner_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    topic = normalize_string(topic)

    academic_level = normalize_string(
        academic_level
    )

    difficulty = normalize_string(
        difficulty
    ).lower()

    if not topic:
        raise ValueError(
            "Topic cannot be empty."
        )

    if not academic_level:
        raise ValueError(
            "Academic level cannot be empty."
        )

    if difficulty not in {
        "basic",
        "standard",
        "advanced",
    }:
        raise ValueError(
            "Difficulty must be basic, standard, "
            "or advanced."
        )

    prompt = build_topic_plan_prompt(
        topic=topic,
        academic_level=academic_level,
        difficulty=difficulty,
        learner_profile=learner_profile,
    )

    raw_result = generate_with_ai(
        prompt,
        expect_json=True,
    )

    data = clean_ai_json(raw_result)

    prerequisites = build_prerequisite_nodes(
        data.get("prerequisites", [])
    )

    main_pages = build_main_page_nodes(
        data.get("main_pages", [])
    )

    validate_topic_plan(
        prerequisites=prerequisites,
        main_pages=main_pages,
    )

    return {
        "plan_source": "generic_ai_topic_planner",
        "topic": topic,
        "academic_level": academic_level,
        "difficulty": difficulty,
        "prerequisites": prerequisites,
        "main_pages": main_pages,
    }