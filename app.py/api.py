import traceback
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Literal
from datetime import datetime, timezone

QUIZ_STORE: dict[str, dict[str, Any]] = {}

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from planners.input_resolver import resolve_topic
from planners.lesson_content_planner import generate_lecture
from planners.lesson_planner import plan_lesson

from utils.database import (
    create_tables,
    load_web_lecture_progress,
    load_web_lecture_topics,
    load_web_quiz_results,
    mark_web_lecture_completed,
    migrate_legacy_dashboard_results,
    save_web_lecture_started,
    save_web_quiz_result,
    update_saved_explore_interest,
)
from services.auth_service import (
    web_login,
    web_signup,
)

from services.knowledge_graph_generator import (
    generate_knowledge_graph,
)

from services.knowledge_graph_service import (
    get_knowledge_graph,
)

from services.profile_service import (
    load_profile,
    save_web_personalization_profile,
)

from modeles.lecture_session import ContentNode

from services.lecture_session_service import (
    create_session,
    get_page as get_cached_page,
    get_session,
    save_page,
    serialize_session,
)

from services.topic_plan_service import (
    build_topic_plan,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    create_tables()
    migrate_legacy_dashboard_results()
    yield


app = FastAPI(
    title="Novateach API",
    version="1.0.0",
    lifespan=lifespan,
)
@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Novateach API",
        "docs": "/docs",
        "health": "/api/health",
    }
# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================


class LoginData(BaseModel):
    username: str
    password: str


class SignupData(BaseModel):
    username: str
    name: str
    password: str


class OnboardingData(BaseModel):
    username: str
    name: str
    understanding_strategy: str
    support_strategy: str
    difficulty_trigger: str
    teaching_strategy: str
    retention_pattern: str
    pace_preference: str
    extra_learning_info: str = ""


class PersonalizationData(BaseModel):
    username: str
    answers: dict
    extra_learning_info: str = ""


class ExploreInterestData(BaseModel):
    username: str
    topic: str
    subject: str
    status: Literal["saved", "later", "remove"]


class ResolveTopicData(BaseModel):
    topic: str
    academic_level: str


class GenerateLessonData(BaseModel):
    username: str
    topic: str
    academic_level: str
    difficulty: str = "standard"
    subject: str | None = None
    topic_profile: dict[str, Any] | None = None

class StartLectureData(BaseModel):
    username: str
    topic: str
    academic_level: str
    difficulty: str = "standard"
    subject: str | None = None
    learner_profile: dict[str, Any] = Field(
        default_factory=dict
    )


class PrefetchPageData(BaseModel):
    page_number: int

class StartPrerequisiteData(BaseModel):
    prerequisite_node_id: str


class LectureCompleteRequest(BaseModel):
    username: str


class DoubtRequest(BaseModel):
    username: str
    question: str
    topic: str = ""
    session_id: str | None = None
    page_number: int | None = None


class QuizGenerateRequest(BaseModel):
    username: str
    topic: str
    session_id: str | None = None
    academic_level: str = ""
    difficulty: str = "standard"
    question_count: int = 5


class QuizSubmitRequest(BaseModel):
    username: str
    quiz_id: str
    answers: dict[str, str]
    lecture_feedback: str = ""

# ============================================================
# SERIALIZATION HELPERS
# ============================================================


def object_to_dict(value):
    if value is None:
        return None

    if isinstance(value, dict):
        return value

    if hasattr(value, "to_dict"):
        result = value.to_dict()

        if isinstance(result, dict):
            return result

    if hasattr(value, "model_dump"):
        result = value.model_dump()

        if isinstance(result, dict):
            return result

    if hasattr(value, "__dict__"):
        return {
            key: object_to_dict(item)
            for key, item in value.__dict__.items()
            if not key.startswith("_")
        }

    return value


def get_topic_profile(resolution) -> dict[str, Any]:
    data = object_to_dict(resolution)

    if not isinstance(data, dict):
        return {}

    return {
        "domain": data.get("domain"),
        "topic_type": data.get("topic_type"),
        "content_modes": data.get(
            "content_modes",
            [],
        ),
        "formula_relevant": data.get(
            "formula_relevant",
        ),
        "quantitative_relevant": data.get(
            "quantitative_relevant",
        ),
    }


def build_resolution_data(resolution) -> dict[str, Any]:
    data = object_to_dict(resolution)

    if not isinstance(data, dict):
        raise ValueError(
            "Topic Resolver returned invalid data."
        )

    return {
        "status": data.get("status"),
        "topic": data.get("topic"),
        "subject": data.get("subject"),
        "possible_subjects": data.get(
            "possible_subjects",
            [],
        ),
        "reason": data.get(
            "reason",
            "",
        ),
        "domain": data.get("domain"),
        "topic_type": data.get("topic_type"),
        "content_modes": data.get(
            "content_modes",
            [],
        ),
        "formula_relevant": data.get(
            "formula_relevant",
        ),
        "quantitative_relevant": data.get(
            "quantitative_relevant",
        ),
    }


# ============================================================
# LECTURE SESSION HELPERS
# ============================================================


def validate_difficulty(difficulty: str) -> str:
    normalized = difficulty.strip().lower()

    if normalized not in {
        "basic",
        "standard",
        "advanced",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "Difficulty must be basic, standard, "
                "or advanced."
            ),
        )

    return normalized


def validate_lecture_session_request(
    data: StartLectureData,
) -> tuple[str, str, str, str]:
    username = data.username.strip()
    topic = data.topic.strip()
    academic_level = data.academic_level.strip()
    difficulty = validate_difficulty(data.difficulty)

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty.",
        )

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty.",
        )

    if not academic_level:
        raise HTTPException(
            status_code=400,
            detail="Academic level cannot be empty.",
        )

    return (
        username,
        topic,
        academic_level,
        difficulty,
    )


def get_current_page_node(
    session,
    page_number: int,
) -> ContentNode:
    node = session.get_page(page_number)

    if node is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Page {page_number} does not exist "
                "in this lecture session."
            ),
        )

    return node


# ============================================================
# HEALTH
# ============================================================


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "novateach-api",
    }


# ============================================================
# AUTH
# ============================================================


@app.post("/api/auth/login")
def login_user(data: LoginData):
    return web_login(
        username=data.username,
        password=data.password,
    )


@app.post("/api/auth/signup")
def signup_user(data: SignupData):
    return web_signup(
        username=data.username,
        name=data.name,
        password=data.password,
    )


# ============================================================
# ONBOARDING QUESTIONS
# ============================================================


@app.get("/api/onboarding/questions")
def get_onboarding_questions():
    return {
        "questions": [
            {
                "key": "understanding_strategy",
                "question": (
                    "What helps you understand something best?"
                ),
                "options": {
                    "A": "A simple explanation",
                    "B": "Examples or analogies",
                    "C": "Visuals or diagrams",
                    "D": "Trying problems myself",
                },
            },
            {
                "key": "support_strategy",
                "question": (
                    "When you get stuck, what helps most?"
                ),
                "options": {
                    "A": "Explain it more simply",
                    "B": "Give me an example",
                    "C": "Break it into smaller steps",
                    "D": "Find exactly where I got confused",
                },
            },
            {
                "key": "difficulty_trigger",
                "question": (
                    "What usually makes a topic difficult for you?"
                ),
                "options": {
                    "A": "Too much information at once",
                    "B": "Missing the basic concepts",
                    "C": (
                        "I understand theory but "
                        "struggle to apply it"
                    ),
                    "D": "I forget what I learned",
                },
            },
            {
                "key": "teaching_strategy",
                "question": (
                    "Which learning flow feels most natural to you?"
                ),
                "options": {
                    "A": "Concept → Example → Practice",
                    "B": "Example → Explanation → Practice",
                    "C": "Visual → Explanation → Practice",
                    "D": "Problem → Concept → Practice",
                },
            },
            {
                "key": "retention_pattern",
                "question": (
                    "What best describes how you remember things?"
                ),
                "options": {
                    "A": (
                        "I remember the main idea "
                        "but forget details"
                    ),
                    "B": (
                        "I remember it better "
                        "after practicing"
                    ),
                    "C": "I need revision to remember it",
                    "D": "I usually remember it well",
                },
            },
            {
                "key": "pace_preference",
                "question": (
                    "How would you like Novateach "
                    "to pace your learning?"
                ),
                "options": {
                    "A": "Slow and detailed",
                    "B": "Moderate",
                    "C": "Fast",
                    "D": (
                        "Adaptive — slow down "
                        "when I struggle"
                    ),
                },
            },
        ]
    }


# ============================================================
# LEGACY ONBOARDING
# ============================================================


@app.post("/api/onboarding")
def submit_onboarding(data: OnboardingData):
    return {
        "status": "success",
        "message": "Onboarding data received.",
        "profile": data.model_dump(),
    }


# ============================================================
# PERSONALIZATION
# ============================================================


@app.post("/api/profile/personalization")
def save_personalization(data: PersonalizationData):
    return save_web_personalization_profile(
        username=data.username,
        answers=data.answers,
        extra_learning_info=data.extra_learning_info,
    )


@app.post("/api/profile/interests")
def update_explore_interest(data: ExploreInterestData):
    username = data.username.strip()
    topic = data.topic.strip()
    subject = data.subject.strip()

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty.",
        )

    if not topic or not subject:
        raise HTTPException(
            status_code=400,
            detail="Topic and subject are required.",
        )

    if load_profile(username) is None:
        raise HTTPException(
            status_code=404,
            detail="Learner profile was not found.",
        )

    try:
        interests = update_saved_explore_interest(
            username=username,
            topic=topic,
            subject=subject,
            status=data.status,
        )
    except Exception as error:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Could not update saved interests: {error}",
        ) from error

    return {
        "status": "success",
        "saved_interests": interests,
    }


# ============================================================
# TOPIC RESOLUTION
# ============================================================


@app.post("/api/lesson/resolve")
def resolve_lesson_topic(data: ResolveTopicData):
    topic = data.topic.strip()
    academic_level = data.academic_level.strip()

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty.",
        )

    if not academic_level:
        raise HTTPException(
            status_code=400,
            detail="Academic level cannot be empty.",
        )

    try:
        resolution = resolve_topic(
            topic=topic,
            academic_level=academic_level,
        )

        return build_resolution_data(resolution)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        print("\n========== TOPIC RESOLUTION ERROR ==========")
        print(f"{type(error).__name__}: {error}")
        traceback.print_exc()
        print("============================================\n")

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ============================================================
# NEW LECTURE SESSION: TABLE OF CONTENTS
# ============================================================


@app.post("/api/lecture/start")
def start_lecture_session(data: StartLectureData):
    username = data.username.strip()
    topic = data.topic.strip()
    academic_level = data.academic_level.strip()
    difficulty = validate_difficulty(data.difficulty)
    selected_subject = (
    data.subject.strip()
    if isinstance(data.subject, str)
    else ""
)
    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty.",
        )

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty.",
        )

    if not academic_level:
        raise HTTPException(
            status_code=400,
            detail="Academic level cannot be empty.",
        )

    try:
        print("\n========== PROGRESSIVE LECTURE START ==========")
        print("Username:", username)
        print("Topic:", topic)
        print("Academic level:", academic_level)
        print("Difficulty:", difficulty)
        print("===============================================")

        print("STAGE 1: Loading learner profile")

        learner_profile = load_profile(username)

        if learner_profile is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Learner profile was not found. "
                    "Please complete personalization first."
                ),
            )

        print("STAGE 1 COMPLETE")

        print("STAGE 2: Resolving topic")

        resolution = resolve_topic(
            topic=topic,
            academic_level=academic_level,
        )

        resolution_data = build_resolution_data(
            resolution
        )

        print(
            "STAGE 2 COMPLETE:",
            resolution_data.get("status"),
        )

        if resolution_data.get("status") == "invalid":
            return {
                "status": "invalid",
                "resolution": resolution_data,
            }

        if (
            resolution_data.get("status") == "ambiguous"
            and not selected_subject
        ):
            return {
                "status": "ambiguous",
                "resolution": resolution_data,
                "message": (
                    "Please select a subject before "
                    "starting the progressive lecture."
                ),
            }

        subject = (
            selected_subject
            or resolution_data.get("subject")
            or ""
        )

        if not subject:
            raise HTTPException(
                status_code=409,
                detail=(
                    "A subject could not be resolved "
                    "for this topic."
                ),
            )

        print("STAGE 2 SUBJECT:", subject)

        topic_profile = get_topic_profile(
            resolution
        )

        print("STAGE 3: Generating knowledge graph")

        graph_id = generate_knowledge_graph(
            topic=topic,
            subject=subject,
            academic_level=academic_level,
        )

        graph = get_knowledge_graph(graph_id)

        print(
            "STAGE 3 COMPLETE: graph_id =",
            graph_id,
        )

        print("STAGE 4: Planning lesson")

        blueprint = plan_lesson(
            topic=topic,
            subject=subject,
            academic_level=academic_level,
            difficulty=difficulty,
            learner_profile=learner_profile,
            topic_profile=topic_profile,
        )

        print("STAGE 4 COMPLETE")

        print("STAGE 5: Building table of contents")

        plan = build_topic_plan(
            topic=topic,
            academic_level=academic_level,
            difficulty=difficulty,
            learner_profile=data.learner_profile,
        )

        print("STAGE 5 COMPLETE")

        session = create_session(
            user_id=username,
            topic=topic,
            academic_level=academic_level,
            difficulty=difficulty,
            prerequisites=plan["prerequisites"],
            main_pages=plan["main_pages"],
            subject=subject,
            topic_profile=topic_profile,
        )
        save_web_lecture_started(
            username=username,
            session_id=session.session_id,
            topic=topic,
        )

        print(
            "SESSION CREATED:",
            session.session_id,
        )

        print("STAGE 6: Generating complete lesson")

        lesson = generate_lecture(
            blueprint=blueprint,
            learner_profile=learner_profile,
        )

        lesson_data = object_to_dict(lesson)

        if not isinstance(lesson_data, dict):
            raise ValueError(
                "Generated lesson could not be converted "
                "into a dictionary."
            )

        print("STAGE 6 COMPLETE")

        print("STAGE 7: Splitting lesson into pages")

        from services.lecture_page_service import (
            split_lesson_into_pages,
        )

        pages = split_lesson_into_pages(
            session=session,
            lesson_data=lesson_data,
        )

        for page_number, page_content in pages.items():
            save_page(
                session_id=session.session_id,
                page_number=page_number,
                content=jsonable_encoder(
                    page_content
                ),
            )

        print("STAGE 7 COMPLETE")

        serialized_session = serialize_session(
            session
        )

        return jsonable_encoder(
            {
                "status": "success",
                "session": serialized_session,
                "graph_id": graph_id,
                "graph": graph,
                "message": (
                    "Progressive lecture session created "
                    "with table of contents and pages."
                ),
            }
        )

    except HTTPException:
        raise

    except ValueError as error:
        print("\n========== PROGRESSIVE LESSON VALIDATION ERROR ==========")
        print(f"{type(error).__name__}: {error}")
        traceback.print_exc()
        print("=========================================================\n")

        raise HTTPException(
            status_code=422,
            detail=str(error),
        )

    except Exception as error:
        print("\n========== PROGRESSIVE LESSON ERROR ==========")
        print(f"{type(error).__name__}: {error}")
        traceback.print_exc()
        print("===============================================\n")

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
# ============================================================
# GET LECTURE SESSION
# ============================================================


@app.get("/api/lecture/{session_id}")
def get_lecture_session(session_id: str):
    session = get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Lecture session not found.",
        )

    return {
        "status": "success",
        "session": serialize_session(session),
    }


@app.post("/api/lecture/{session_id}/complete")
def complete_lecture(
    session_id: str,
    data: LectureCompleteRequest,
):
    session = get_session(session_id)

    if session is None or session.user_id != data.username:
        raise HTTPException(
            status_code=404,
            detail="Lecture session not found.",
        )

    if session.session_type == "prerequisite":
        raise HTTPException(
            status_code=400,
            detail="Prerequisite lessons are not tracked as main lectures.",
        )

    if not mark_web_lecture_completed(data.username, session_id):
        raise HTTPException(
            status_code=404,
            detail="Lecture progress record was not found.",
        )

    return {
        "status": "success",
        "session_id": session_id,
        "completed": True,
    }


# ============================================================
# GET LECTURE PAGE
# ============================================================

@app.post(
    "/api/lecture/{session_id}/prerequisite/start"
)
def start_prerequisite_lecture(
    session_id: str,
    data: StartPrerequisiteData,
):
    parent_session = get_session(session_id)

    if parent_session is None:
        raise HTTPException(
            status_code=404,
            detail="Parent lecture session not found.",
        )

    prerequisite = next(
        (
            item
            for item in parent_session.prerequisites
            if item.node_id == data.prerequisite_node_id
        ),
        None,
    )

    if prerequisite is None:
        raise HTTPException(
            status_code=404,
            detail="Prerequisite not found in this session.",
        )

    learner_profile = load_profile(
        parent_session.user_id
    )

    if learner_profile is None:
        raise HTTPException(
            status_code=404,
            detail="Learner profile not found.",
        )

    try:
        print(
            "\n========== PREREQUISITE START =========="
        )
        print("Parent session:", parent_session.session_id)
        print("Prerequisite:", prerequisite.title)

        child_plan = build_topic_plan(
            topic=prerequisite.title,
            academic_level=parent_session.academic_level,
            difficulty="basic",
            learner_profile={},
        )

        child_session = create_session(
            user_id=parent_session.user_id,
            topic=prerequisite.title,
            academic_level=parent_session.academic_level,
            difficulty="basic",
            prerequisites=child_plan["prerequisites"],
            main_pages=child_plan["main_pages"],
            subject=parent_session.subject,
            topic_profile=parent_session.topic_profile,
            session_type="prerequisite",
            parent_session_id=parent_session.session_id,
            prerequisite_node_id=prerequisite.node_id,
            return_page=parent_session.current_page,
        )

        print(
            "CHILD SESSION CREATED:",
            child_session.session_id,
        )

        child_resolution = resolve_topic(
            topic=prerequisite.title,
            academic_level=parent_session.academic_level,
        )

        child_resolution_data = build_resolution_data(
            child_resolution
        )

        child_subject = (
            child_resolution_data.get("subject")
            or parent_session.subject
            or "General"
        )

        child_topic_profile = get_topic_profile(
            child_resolution
        )

        child_blueprint = plan_lesson(
            topic=prerequisite.title,
            subject=child_subject,
            academic_level=parent_session.academic_level,
            difficulty="basic",
            learner_profile=learner_profile,
            topic_profile=child_topic_profile,
        )

        child_lesson = generate_lecture(
            blueprint=child_blueprint,
            learner_profile=learner_profile,
        )

        child_lesson_data = object_to_dict(
            child_lesson
        )

        if not isinstance(child_lesson_data, dict):
            raise ValueError(
                "Prerequisite lesson could not be "
                "converted into a dictionary."
            )

        from services.lecture_page_service import (
            split_lesson_into_pages,
        )

        child_pages = split_lesson_into_pages(
            session=child_session,
            lesson_data=child_lesson_data,
        )

        if not child_pages:
            raise ValueError(
                "Prerequisite lesson generated no pages."
            )

        for page_number, page_content in (
            child_pages.items()
        ):
            save_page(
                session_id=child_session.session_id,
                page_number=page_number,
                content=jsonable_encoder(
                    page_content
                ),
            )

        print(
            "PREREQUISITE PAGES GENERATED:",
            len(child_pages),
        )

        serialized_child = serialize_session(
            child_session
        )

        return jsonable_encoder(
            {
                "status": "success",
                "session": serialized_child,
                "return_to_session_id": (
                    parent_session.session_id
                ),
                "return_page": (
                    parent_session.current_page
                ),
                "message": (
                    "Prerequisite lecture created "
                    "and page 1 generated."
                ),
            }
        )

    except HTTPException:
        raise

    except ValueError as error:
        print(
            "\n========== PREREQUISITE VALIDATION ERROR =========="
        )
        print(f"{type(error).__name__}: {error}")
        traceback.print_exc()
        print(
            "====================================================\n"
        )

        raise HTTPException(
            status_code=422,
            detail=str(error),
        )

    except Exception as error:
        print(
            "\n========== PREREQUISITE GENERATION ERROR =========="
        )
        print(f"{type(error).__name__}: {error}")
        traceback.print_exc()
        print(
            "===================================================\n"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not generate prerequisite lecture: "
                f"{error}"
            ),
        )
# ============================================================
# GET LECTURE PAGE
# ============================================================


@app.get("/api/lecture/{session_id}/page/{page_number}")
def get_lecture_page(
    session_id: str,
    page_number: int,
):
    session = get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Lecture session not found.",
        )

    if page_number < 1:
        raise HTTPException(
            status_code=400,
            detail="Page number must be at least 1.",
        )

    node = get_current_page_node(
        session=session,
        page_number=page_number,
    )

    cached_page = get_cached_page(
        session_id=session_id,
        page_number=page_number,
    )

    if cached_page is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "This page is planned but has not "
                "been generated."
            ),
        )

    is_final_page = (
        page_number == len(session.main_pages)
    )

    return jsonable_encoder(
        {
            "status": "ready",
            "session_id": session_id,
            "page_number": page_number,
            "total_pages": len(session.main_pages),
            "is_final_page": is_final_page,
            "next_page_number": (
                page_number + 1
                if not is_final_page
                else None
            ),
            "quiz_available": is_final_page,
            "node": {
                "node_id": node.node_id,
                "title": node.title,
                "objective": node.objective,
                "display_number": node.display_number,
            },
            "page": cached_page,
        }
    )
# ============================================================
# PREFETCH LECTURE PAGE
# ============================================================


@app.post("/api/lecture/{session_id}/prefetch")
def prefetch_lecture_page(
    session_id: str,
    data: PrefetchPageData,
):
    session = get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Lecture session not found.",
        )

    if data.page_number < 1:
        raise HTTPException(
            status_code=400,
            detail="Page number must be at least 1.",
        )

    node = get_current_page_node(
        session=session,
        page_number=data.page_number,
    )

    cached_page = get_cached_page(
        session_id=session_id,
        page_number=data.page_number,
    )

    if cached_page is not None:
        return {
            "status": "already_ready",
            "session_id": session_id,
            "page_number": data.page_number,
            "page": cached_page,
        }

    return {
        "status": "planned",
        "session_id": session_id,
        "page_number": data.page_number,
        "node": {
            "node_id": node.node_id,
            "title": node.title,
            "objective": node.objective,
        },
        "message": (
            "This page is planned and will be "
            "connected to generation next."
        ),
    }

# ============================================================
# COMPLETE LESSON + KNOWLEDGE GRAPH
# ============================================================


@app.post("/api/lesson/generate")
def generate_lesson(data: GenerateLessonData):
    username = data.username.strip()
    topic = data.topic.strip()
    academic_level = data.academic_level.strip()
    difficulty = data.difficulty.strip().lower()

    selected_subject = (
        data.subject.strip()
        if isinstance(data.subject, str)
        else ""
    )

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty.",
        )

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty.",
        )

    if not academic_level:
        raise HTTPException(
            status_code=400,
            detail="Academic level cannot be empty.",
        )

    if difficulty not in {
        "basic",
        "standard",
        "advanced",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "Difficulty must be basic, standard, "
                "or advanced."
            ),
        )

    try:
        print("\n========== LESSON REQUEST ==========")
        print("Username:", username)
        print("Topic:", topic)
        print("Academic level:", academic_level)
        print("Difficulty:", difficulty)
        print("Selected subject:", selected_subject)
        print("====================================")

        print("STAGE 1: Loading learner profile")

        learner_profile = load_profile(username)

        if learner_profile is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Learner profile was not found. "
                    "Please complete personalization first."
                ),
            )

        print("STAGE 1 COMPLETE")

        print("STAGE 2: Resolving topic")

        resolution = resolve_topic(
            topic=topic,
            academic_level=academic_level,
        )

        resolution_data = build_resolution_data(
            resolution
        )

        print(
            "STAGE 2 COMPLETE:",
            resolution_data.get("status"),
        )

        if resolution_data.get("status") == "invalid":
            return {
                "status": "invalid",
                "resolution": resolution_data,
            }

        if (
            resolution_data.get("status") == "ambiguous"
            and not selected_subject
        ):
            return {
                "status": "ambiguous",
                "resolution": resolution_data,
            }

        subject = selected_subject or resolution_data.get(
            "subject"
        )

        if not subject:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Please choose a subject before "
                    "generating this lesson."
                ),
            )

        topic_profile = data.topic_profile

        if not isinstance(topic_profile, dict):
            topic_profile = get_topic_profile(
                resolution
            )

        print("STAGE 3: Generating or loading knowledge graph")

        graph_id = generate_knowledge_graph(
            topic=topic,
            subject=subject,
            academic_level=academic_level,
        )

        graph = get_knowledge_graph(graph_id)

        print(
            "STAGE 3 COMPLETE: graph_id =",
            graph_id,
        )

        print("STAGE 4: Planning lesson")

        blueprint = plan_lesson(
            topic=topic,
            subject=subject,
            academic_level=academic_level,
            difficulty=difficulty,
            learner_profile=learner_profile,
            topic_profile=topic_profile,
        )

        print("STAGE 4 COMPLETE")

        print("STAGE 5: Generating lecture")

        lesson = generate_lecture(
            blueprint=blueprint,
            learner_profile=learner_profile,
        )

        print("STAGE 5 COMPLETE")

        print("LESSON PIPELINE COMPLETE")

        return {
            "status": "success",
            "request": {
                "username": username,
                "topic": topic,
                "subject": subject,
                "academic_level": academic_level,
                "difficulty": difficulty,
            },
            "resolution": resolution_data,
            "graph_id": graph_id,
            "graph": graph,
            "blueprint": blueprint.to_dict(),
            "lesson": lesson.to_dict(),
        }

    except HTTPException:
        raise

    except ValueError as error:
        print("\n========== LESSON VALIDATION ERROR ==========")
        print(f"{type(error).__name__}: {error}")
        traceback.print_exc()
        print("=============================================\n")

        raise HTTPException(
            status_code=422,
            detail=str(error),
        )

    except Exception as error:
        print("\n========== LESSON PIPELINE ERROR ==========")
        print(f"{type(error).__name__}: {error}")
        traceback.print_exc()
        print("===========================================\n")

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

def safe_ai_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def build_doubt_prompt(data: DoubtRequest) -> str:
    return f"""
You are Novateach, a patient personal tutor.

Topic:
{data.topic or "Not provided"}

Student question:
{data.question}

Explain the answer clearly for the student's level.

Return valid JSON with exactly these keys:
{{
  "answer": "Clear explanation",
  "simpler_explanation": "Simpler version",
  "analogy": "Helpful analogy",
  "next_question": "One short follow-up question"
}}

Return only JSON.
""".strip()


def build_quiz_prompt(
    data: QuizGenerateRequest,
) -> str:
    count = max(3, min(data.question_count, 10))

    return f"""
Create a quiz for a student.

Topic:
{data.topic}

Academic level:
{data.academic_level or "Not provided"}

Difficulty:
{data.difficulty}

Create exactly {count} multiple-choice questions.

Return valid JSON in exactly this format:
{{
  "title": "Quiz title",
  "questions": [
    {{
      "id": "q1",
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Why this answer is correct"
    }}
  ]
}}

Rules:
- Exactly {count} questions.
- Every question must have four options.
- correct_answer must exactly match one option.
- Return only JSON.
""".strip()


def calculate_quiz_result(
    quiz: dict[str, Any],
    answers: dict[str, str],
) -> dict[str, Any]:
    questions = quiz.get("questions", [])

    correct = 0
    results = []

    for question in questions:
        question_id = str(
            question.get("id", "")
        )

        expected = safe_ai_text(
            question.get("correct_answer")
        )

        submitted = safe_ai_text(
            answers.get(question_id)
        )

        is_correct = (
            submitted.lower()
            == expected.lower()
        )

        if is_correct:
            correct += 1

        results.append(
            {
                "question_id": question_id,
                "submitted_answer": submitted,
                "correct_answer": expected,
                "correct": is_correct,
                "explanation": question.get(
                    "explanation",
                    "",
                ),
            }
        )

    total = len(questions)
    score = (
        round((correct / total) * 100)
        if total
        else 0
    )

    return {
        "correct": correct,
        "total": total,
        "score": score,
        "results": results,
        "next_step": (
            "Continue to the next topic."
            if score >= 70
            else "Review this topic and try a short retest."
        ),
    }


@app.post("/api/doubt/resolve")
def resolve_doubt(data: DoubtRequest):
    if not data.username.strip():
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty.",
        )

    if not data.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        from ai_generator import generate_with_ai

        response = generate_with_ai(
            build_doubt_prompt(data),
            expect_json=True,
        )

        if not isinstance(response, dict):
            raise ValueError(
                "Doubt resolver returned invalid data.",
            )

        return {
            "status": "success",
            "topic": data.topic,
            "response": response,
        }

    except Exception as error:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Could not resolve doubt: {error}",
        )

@app.post("/api/quiz/generate")
def generate_quiz(data: QuizGenerateRequest):
    if not data.username.strip():
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty.",
        )

    if not data.topic.strip():
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty.",
        )

    try:
        from ai_generator import generate_with_ai

        quiz = generate_with_ai(
            build_quiz_prompt(data),
            expect_json=True,
        )

        if not isinstance(quiz, dict):
            raise ValueError(
                "Quiz generator returned invalid data.",
            )

        questions = quiz.get(
            "questions",
            [],
        )

        if not isinstance(questions, list) or not questions:
            raise ValueError(
                "Quiz questions are invalid.",
            )

        normalized_questions = []
        question_ids = set()
        quiz_payload_questions = []

        for index, question in enumerate(questions):
            if not isinstance(question, dict):
                raise ValueError("Quiz question data is invalid.")

            question_id = str(question.get("id") or f"q{index + 1}")
            question_text = safe_ai_text(question.get("question"))
            options = question.get("options")
            correct_answer = safe_ai_text(question.get("correct_answer"))

            if (
                not question_text
                or not isinstance(options, list)
                or len(options) < 2
                or not all(isinstance(option, str) and option.strip() for option in options)
                or not correct_answer
                or correct_answer.casefold()
                not in {option.casefold() for option in options}
                or question_id in question_ids
            ):
                raise ValueError("Quiz question data is invalid.")

            normalized_question = {
                **question,
                "id": question_id,
                "question": question_text,
                "options": options,
                "correct_answer": correct_answer,
            }
            normalized_questions.append(normalized_question)
            quiz_payload_questions.append(
                {
                    "id": question_id,
                    "question": question_text,
                    "options": options,
                }
            )
            question_ids.add(question_id)

        scored_quiz = {
            **quiz,
            "questions": normalized_questions,
        }

        quiz_id = (
            f"{data.username}-"
            f"{datetime.now(timezone.utc).timestamp()}"
        )

        quiz_payload = {
            "status": "success",
            "quiz_id": quiz_id,
            "topic": data.topic,
            "difficulty": data.difficulty,
            "title": quiz.get(
                "title",
                f"{data.topic} Quiz",
            ),
            "questions": quiz_payload_questions,
        }

        QUIZ_STORE[quiz_id] = {
            "username": data.username,
            "topic": data.topic,
            "quiz": scored_quiz,
        }

        return quiz_payload

    except Exception as error:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Could not generate quiz: {error}",
        )

@app.post("/api/quiz/submit")
def submit_quiz(data: QuizSubmitRequest):
    stored = QUIZ_STORE.get(data.quiz_id)

    if stored is None:
        raise HTTPException(
            status_code=404,
            detail="Quiz session has expired.",
        )

    if stored["username"] != data.username:
        raise HTTPException(
            status_code=403,
            detail="This quiz does not belong to this user.",
        )

    questions = stored["quiz"]["questions"]
    expected_ids = {str(question["id"]) for question in questions}

    if set(data.answers) != expected_ids:
        raise HTTPException(
            status_code=400,
            detail="Please answer every quiz question before submitting.",
        )

    options_by_id = {
        str(question["id"]): question["options"]
        for question in questions
    }
    if any(
        answer not in options_by_id[question_id]
        for question_id, answer in data.answers.items()
    ):
        raise HTTPException(
            status_code=400,
            detail="One or more submitted answers are invalid.",
        )

    result = calculate_quiz_result(
        quiz=stored["quiz"],
        answers=data.answers,
    )

    save_web_quiz_result(
        username=data.username,
        quiz_id=data.quiz_id,
        topic=stored["topic"],
        score=result["score"],
        correct_count=result["correct"],
        total_questions=result["total"],
        feedback=data.lecture_feedback.strip(),
        next_step=result["next_step"],
    )

    return {
        "status": "success",
        "quiz_id": data.quiz_id,
        "topic": stored["topic"],
        **result,
    }

@app.get("/api/dashboard/{username}")
def get_dashboard(username: str):
    username = username.strip()

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty.",
        )

    results = load_web_quiz_results(
        username,
    )

    total_quizzes = len(results)

    average_score = (
        round(
            sum(
                item["score"]
                for item in results
            )
            / total_quizzes
        )
        if total_quizzes
        else 0
    )

    profile = load_profile(username)
    profile_data = (
        profile.get_personalization_summary()
        if profile is not None
        else None
    )
    lecture_progress = load_web_lecture_progress(username)

    topic_scores: dict[str, list[int]] = {}
    for result in results:
        topic_scores.setdefault(result["topic"], []).append(result["score"])

    topic_averages = {
        topic_name: round(sum(scores) / len(scores))
        for topic_name, scores in topic_scores.items()
    }
    topics_studied = len(
        set(topic_scores)
        | {
            row["topic"]
            for row in load_web_lecture_topics(username)
        }
    )
    strongest_topics = [
        topic_name
        for topic_name, score in topic_averages.items()
        if score >= 80
    ]
    topics_to_review = [
        topic_name
        for topic_name, score in topic_averages.items()
        if score < 70
    ]

    return {
        "status": "success",
        "username": username,
        "profile": profile_data,
        "stats": {
            **lecture_progress,
            "quizzes_completed": total_quizzes,
            "average_score": average_score,
            "topics_completed": len(topic_scores),
            "topics_studied": topics_studied,
        },
        "strongest_topics": strongest_topics,
        "topics_to_review": topics_to_review,
        "quiz_history": [
            {
                "quiz_id": item["quiz_id"],
                "topic": item["topic"],
                "score": item["score"],
                "correct": item["correct_count"],
                "total": item["total_questions"],
                "feedback": item["feedback"],
                "next_step": item["next_step"],
                "created_at": item["created_at"],
            }
            for item in results
        ],
        "next_step": (
            results[0]["next_step"]
            if results
            else "Start your first lesson."
        ),
    }