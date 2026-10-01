from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi.encoders import jsonable_encoder

from modeles.lecture_session import (
    ContentNode,
    LectureSession,
)


_SESSIONS: dict[str, LectureSession] = {}

_PAGE_CACHE: dict[
    tuple[str, int],
    dict[str, Any],
] = {}


def create_session(
    user_id: str,
    topic: str,
    academic_level: str,
    difficulty: str,
    prerequisites: list[ContentNode],
    main_pages: list[ContentNode],
    subject: str = "",
    topic_profile: dict[str, Any] | None = None,
    session_type: str = "main",
    parent_session_id: str | None = None,
    prerequisite_node_id: str | None = None,
    return_page: int | None = None,
) -> LectureSession:
    session = LectureSession(
        session_id=f"lecture_{uuid4().hex[:12]}",
        user_id=user_id,
        topic=topic,
        academic_level=academic_level,
        difficulty=difficulty,
        subject=subject,
        topic_profile=topic_profile or {},
        prerequisites=prerequisites,
        main_pages=main_pages,
        current_page=1,
        active_node_id=(
            main_pages[0].node_id
            if main_pages
            else None
        ),
        session_type=session_type,
        parent_session_id=parent_session_id,
        prerequisite_node_id=prerequisite_node_id,
        return_page=return_page,
    )

    _SESSIONS[session.session_id] = session

    return session

def get_session(
    session_id: str,
) -> LectureSession | None:
    return _SESSIONS.get(session_id)


def save_page(
    session_id: str,
    page_number: int,
    content: dict[str, Any],
) -> None:
    _PAGE_CACHE[(session_id, page_number)] = content


def get_page(
    session_id: str,
    page_number: int,
) -> dict[str, Any] | None:
    return _PAGE_CACHE.get(
        (session_id, page_number)
    )


def serialize_node(
    node: ContentNode,
) -> dict[str, Any]:
    result = {
        "node_id": node.node_id,
        "title": node.title,
        "display_number": node.display_number,
        "node_type": node.node_type,
        "objective": node.objective,
        "status": node.status,
        "reason": node.reason,
        "estimated_minutes": node.estimated_minutes,
        "content": node.content,
    }

    return jsonable_encoder(result)
def serialize_session(
    session: LectureSession,
) -> dict[str, Any]:
    pages = {}

    for node in session.main_pages:
        cached = get_page(
            session_id=session.session_id,
            page_number=node.display_number,
        )

        if cached is not None:
            pages[str(node.display_number)] = cached

    result = {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "topic": session.topic,
        "academic_level": session.academic_level,
        "difficulty": session.difficulty,
        "subject": session.subject,
        "topic_profile": session.topic_profile,
        "current_page": session.current_page,
        "active_node_id": session.active_node_id,
        "status": session.status,
        "prerequisites": [
            serialize_node(node)
            for node in session.prerequisites
        ],
        "main_pages": [
            serialize_node(node)
            for node in session.main_pages
        ],
        "pages": pages,
        "session_type": session.session_type,
"parent_session_id": session.parent_session_id,
"prerequisite_node_id": session.prerequisite_node_id,
"return_page": session.return_page,
    }

    return jsonable_encoder(result)