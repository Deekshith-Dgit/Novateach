from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContentNode:
    node_id: str
    title: str
    display_number: int
    node_type: str
    objective: str
    status: str = "upcoming"
    reason: str = ""
    estimated_minutes: int = 8
    content: dict[str, Any] | None = None


@dataclass
class LectureSession:
    session_id: str
    user_id: str
    topic: str
    academic_level: str
    difficulty: str

    subject: str = ""
    topic_profile: dict[str, Any] = field(
        default_factory=dict
    )

    prerequisites: list[ContentNode] = field(
        default_factory=list
    )
    main_pages: list[ContentNode] = field(
        default_factory=list
    )

    current_page: int = 1
    active_node_id: str | None = None

    session_type: str = "main"
    parent_session_id: str | None = None
    prerequisite_node_id: str | None = None
    return_page: int | None = None

    status: str = "active"

    def all_contents(self):
        return self.prerequisites + self.main_pages

    def get_page(self, page_number: int):
        for page in self.main_pages:
            if page.display_number == page_number:
                return page

        return None