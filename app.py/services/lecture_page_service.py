from __future__ import annotations

from typing import Any

from modeles.lesson_plan import LearningBlueprint
from planners.lesson_content_planner import generate_lecture

from modeles.lecture_session import ContentNode, LectureSession
from services.lecture_session_service import (
    get_page,
    save_page,
)


def object_to_dict(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, dict):
        return value

    if hasattr(value, "to_dict"):
        result = value.to_dict()

        if isinstance(result, dict):
            return result

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "__dict__"):
        return {
            key: object_to_dict(item)
            for key, item in value.__dict__.items()
            if not key.startswith("_")
        }

    return value


def get_blueprint_dict(
    blueprint: Any,
) -> dict[str, Any]:
    if hasattr(blueprint, "to_dict"):
        data = blueprint.to_dict()

        if isinstance(data, dict):
            return data

    data = object_to_dict(blueprint)

    if isinstance(data, dict):
        return data

    return {}


def get_learner_profile_data(
    learner_profile: Any,
) -> dict[str, Any]:
    if learner_profile is None:
        return {}

    if isinstance(learner_profile, dict):
        return learner_profile

    if hasattr(learner_profile, "to_dict"):
        data = learner_profile.to_dict()

        if isinstance(data, dict):
            return data

    if hasattr(learner_profile, "__dict__"):
        return {
            key: object_to_dict(value)
            for key, value in learner_profile.__dict__.items()
            if not key.startswith("_")
        }

    return {}


def get_sections(
    lesson_data: dict[str, Any],
) -> list[dict[str, Any]]:
    sections = lesson_data.get("sections", [])

    if not isinstance(sections, list):
        return []

    valid_sections = []

    for section in sections:
        if isinstance(section, dict):
            valid_sections.append(section)

    return valid_sections


def section_to_page_content(
    lesson_data: dict[str, Any],
    section: dict[str, Any],
    page_number: int,
    node: ContentNode,
) -> dict[str, Any]:
    return {
        "page_number": page_number,
        "node_id": node.node_id,
        "title": node.title,
        "objective": node.objective,
        "topic": lesson_data.get("topic", ""),
        "subject": lesson_data.get("subject", ""),
        "academic_level": lesson_data.get(
            "academic_level",
            "",
        ),
        "difficulty": lesson_data.get(
            "difficulty",
            "",
        ),
        "introduction": lesson_data.get(
            "introduction",
            "",
        ),
        "learning_objectives": lesson_data.get(
            "learning_objectives",
            [],
        ),
        "prerequisites": lesson_data.get(
            "prerequisites",
            [],
        ),
        "section": section,
        "final_summary": lesson_data.get(
            "final_summary",
            [],
        ),
        "quiz_metadata": lesson_data.get(
            "quiz_metadata",
            {},
        ),
        "generation_mode": "section_page",
    }


def create_fallback_page(
    lesson_data: dict[str, Any],
    page_number: int,
    node: ContentNode,
) -> dict[str, Any]:
    return {
        "page_number": page_number,
        "node_id": node.node_id,
        "title": node.title,
        "objective": node.objective,
        "topic": lesson_data.get("topic", ""),
        "subject": lesson_data.get("subject", ""),
        "academic_level": lesson_data.get(
            "academic_level",
            "",
        ),
        "difficulty": lesson_data.get(
            "difficulty",
            "",
        ),
        "introduction": lesson_data.get(
            "introduction",
            "",
        ),
        "learning_objectives": lesson_data.get(
            "learning_objectives",
            [],
        ),
        "prerequisites": lesson_data.get(
            "prerequisites",
            [],
        ),
        "section": {
            "section_id": f"section_{page_number}",
            "heading": node.title,
            "purpose": node.objective,
            "explanation": (
                "This section is being prepared from "
                "the generated lesson."
            ),
            "intuition": "",
            "analogy": "",
            "formula_explanation": "",
            "derivation": "",
            "worked_examples": [],
            "common_mistakes": [],
            "retrieval_checkpoint": {},
            "concept_ids": [node.node_id],
        },
        "final_summary": lesson_data.get(
            "final_summary",
            [],
        ),
        "quiz_metadata": lesson_data.get(
            "quiz_metadata",
            {},
        ),
        "generation_mode": "fallback_page",
    }


def generate_complete_lesson_data(
    session: LectureSession,
    blueprint: LearningBlueprint,
    learner_profile: Any,
) -> dict[str, Any]:
    lesson = generate_lecture(
        blueprint=blueprint,
        learner_profile=learner_profile,
    )

    lesson_data = object_to_dict(lesson)

    if not isinstance(lesson_data, dict):
        raise ValueError(
            "Generated lesson could not be converted to a dictionary."
        )

    return lesson_data


def split_lesson_into_pages(
    session: LectureSession,
    lesson_data: dict[str, Any],
) -> dict[int, dict[str, Any]]:
    sections = get_sections(lesson_data)
    pages: dict[int, dict[str, Any]] = {}

    for page_node in session.main_pages:
        page_number = page_node.display_number
        section_index = page_number - 1

        if 0 <= section_index < len(sections):
            pages[page_number] = section_to_page_content(
                lesson_data=lesson_data,
                section=sections[section_index],
                page_number=page_number,
                node=page_node,
            )
        else:
            pages[page_number] = create_fallback_page(
                lesson_data=lesson_data,
                page_number=page_number,
                node=page_node,
            )

    return pages


def ensure_pages_generated(
    session: LectureSession,
    blueprint: LearningBlueprint,
    learner_profile: Any,
) -> dict[int, dict[str, Any]]:
    existing_pages: dict[int, dict[str, Any]] = {}

    for node in session.main_pages:
        page_number = node.display_number
        cached = get_page(
            session_id=session.session_id,
            page_number=page_number,
        )

        if cached is not None:
            existing_pages[page_number] = cached

    if len(existing_pages) == len(session.main_pages):
        return existing_pages

    lesson_data = generate_complete_lesson_data(
        session=session,
        blueprint=blueprint,
        learner_profile=learner_profile,
    )

    generated_pages = split_lesson_into_pages(
        session=session,
        lesson_data=lesson_data,
    )

    for page_number, page_content in generated_pages.items():
        save_page(
            session_id=session.session_id,
            page_number=page_number,
            content=page_content,
        )

    return generated_pages


def generate_single_page(
    session: LectureSession,
    page_number: int,
    blueprint: LearningBlueprint,
    learner_profile: Any,
) -> dict[str, Any]:
    cached = get_page(
        session_id=session.session_id,
        page_number=page_number,
    )

    if cached is not None:
        return cached

    all_pages = ensure_pages_generated(
        session=session,
        blueprint=blueprint,
        learner_profile=learner_profile,
    )

    page = all_pages.get(page_number)

    if page is None:
        raise ValueError(
            f"Could not generate page {page_number}."
        )

    return page