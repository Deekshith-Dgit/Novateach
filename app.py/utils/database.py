import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "novateach.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ============================================================
# DATABASE MIGRATIONS
# ============================================================

def migrate_users_table(conn: sqlite3.Connection) -> None:
    """
    Add newer columns to an existing users table safely.

    CREATE TABLE IF NOT EXISTS does not alter an existing SQLite table.
    This migration lets you keep your existing novateach.db and users.
    """

    columns = {
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(users)"
        ).fetchall()
    }

    if "password_hash" not in columns:
        conn.execute(
            """
            ALTER TABLE users
            ADD COLUMN password_hash TEXT
            """
        )

    if "onboarding_complete" not in columns:
        conn.execute(
            """
            ALTER TABLE users
            ADD COLUMN onboarding_complete INTEGER DEFAULT 0
            """
        )


# ============================================================
# CREATE ALL TABLES
# ============================================================

def create_tables() -> None:
    """
    Create all database tables required by Novateach.

    Existing data is preserved.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ========================================================
        # 1. USERS
        # ========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT UNIQUE NOT NULL,

                name TEXT NOT NULL,

                password_hash TEXT,

                full_profile TEXT DEFAULT '',

                onboarding_complete INTEGER DEFAULT 0,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Upgrade older databases created before auth/onboarding.
        migrate_users_table(conn)

        # ========================================================
        # 2. USER PERSONALIZATION PROFILES
        #
        # Stores "YOU TOLD US" onboarding data.
        # Do not mix this with quiz-derived learner evidence.
        # ========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_personalization_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT UNIQUE NOT NULL,

                answers_json TEXT NOT NULL,

                extra_learning_info TEXT DEFAULT '',

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (username)
                    REFERENCES users(username)
                    ON DELETE CASCADE,

                UNIQUE(username)
            )
            """
        )

        # ========================================================
        # 3. KNOWLEDGE GRAPHS
        # ========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_graphs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                graph_key TEXT UNIQUE NOT NULL,

                topic TEXT NOT NULL,

                subject TEXT,

                academic_level TEXT,

                graph_data TEXT NOT NULL,

                version INTEGER DEFAULT 1,

                status TEXT DEFAULT 'validated',

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # ========================================================
        # 4. CONCEPTS
        # ========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                graph_id INTEGER NOT NULL,

                concept_key TEXT NOT NULL,

                name TEXT NOT NULL,

                description TEXT,

                concept_type TEXT,

                importance TEXT DEFAULT 'normal',

                metadata TEXT,

                FOREIGN KEY (graph_id)
                    REFERENCES knowledge_graphs(id)
                    ON DELETE CASCADE,

                UNIQUE(graph_id, concept_key)
            )
            """
        )

        # ========================================================
        # 5. CONCEPT RELATIONSHIPS
        # ========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS concept_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                graph_id INTEGER NOT NULL,

                from_concept_id INTEGER NOT NULL,

                to_concept_id INTEGER NOT NULL,

                relationship_type TEXT NOT NULL,

                confidence REAL DEFAULT 1.0,

                FOREIGN KEY (graph_id)
                    REFERENCES knowledge_graphs(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (from_concept_id)
                    REFERENCES concepts(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (to_concept_id)
                    REFERENCES concepts(id)
                    ON DELETE CASCADE,

                UNIQUE(
                    graph_id,
                    from_concept_id,
                    to_concept_id,
                    relationship_type
                )
            )
            """
        )

        # ========================================================
        # 6. QUESTIONS
        # ========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                question_key TEXT UNIQUE NOT NULL,

                graph_id INTEGER NOT NULL,

                concept_id INTEGER NOT NULL,

                question_text TEXT NOT NULL,

                question_type TEXT NOT NULL,

                cognitive_skill TEXT NOT NULL,

                difficulty TEXT NOT NULL,

                answer_format TEXT NOT NULL,

                expected_answer TEXT NOT NULL,

                explanation TEXT,

                possible_error_types TEXT,

                prerequisite_concepts TEXT,

                validation_status TEXT DEFAULT 'pending',

                generation_source TEXT DEFAULT 'ai',

                metadata TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (graph_id)
                    REFERENCES knowledge_graphs(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (concept_id)
                    REFERENCES concepts(id)
                    ON DELETE CASCADE
            )
            """
        )

        # ========================================================
        # 7. QUIZ SESSIONS
        # ========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT NOT NULL,

                topic TEXT NOT NULL,

                graph_id INTEGER,

                purpose TEXT NOT NULL,

                difficulty TEXT,

                question_count INTEGER DEFAULT 0,

                completed INTEGER DEFAULT 0,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                completed_at TIMESTAMP,

                FOREIGN KEY (username)
                    REFERENCES users(username)
                    ON DELETE CASCADE,

                FOREIGN KEY (graph_id)
                    REFERENCES knowledge_graphs(id)
                    ON DELETE SET NULL
            )
            """
        )

        # ========================================================
        # 8. WEB QUIZ RESULTS
        # ========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS web_quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT NOT NULL,

                quiz_id TEXT NOT NULL UNIQUE,

                topic TEXT NOT NULL,

                score INTEGER NOT NULL,

                correct_count INTEGER NOT NULL,

                total_questions INTEGER NOT NULL,

                feedback TEXT NOT NULL DEFAULT '',

                next_step TEXT NOT NULL DEFAULT '',

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (username)
                    REFERENCES users(username)
                    ON DELETE CASCADE
            )
            """
        )

        # ========================================================
        # 9. WEB LECTURE PROGRESS
        # ========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS web_lecture_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT NOT NULL,

                session_id TEXT NOT NULL UNIQUE,

                topic TEXT NOT NULL,

                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                completed_at TIMESTAMP,

                FOREIGN KEY (username)
                    REFERENCES users(username)
                    ON DELETE CASCADE
            )
            """
        )

        # ========================================================
        # 10. QUIZ EVIDENCE
        # ========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT NOT NULL,

                session_id INTEGER NOT NULL,

                question_id INTEGER NOT NULL,

                concept_id INTEGER NOT NULL,

                result TEXT NOT NULL,

                student_answer TEXT,

                correct_answer TEXT,

                question_type TEXT,

                cognitive_skill TEXT,

                difficulty TEXT,

                error_category TEXT,

                diagnosis_confidence REAL,

                used_hint INTEGER DEFAULT 0,

                response_time_seconds REAL,

                evaluator_notes TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (username)
                    REFERENCES users(username)
                    ON DELETE CASCADE,

                FOREIGN KEY (session_id)
                    REFERENCES quiz_sessions(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (question_id)
                    REFERENCES questions(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (concept_id)
                    REFERENCES concepts(id)
                    ON DELETE CASCADE
            )
            """
        )

        # ========================================================
        # 9. LEARNER CONCEPT STATE
        # ========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS learner_concept_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT NOT NULL,

                concept_id INTEGER NOT NULL,

                mastery REAL DEFAULT 0.0,

                confidence REAL DEFAULT 0.0,

                evidence_count INTEGER DEFAULT 0,

                recent_accuracy REAL,

                trend TEXT DEFAULT 'unknown',

                status TEXT DEFAULT 'not_started',

                last_evidence_at TIMESTAMP,

                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (username)
                    REFERENCES users(username)
                    ON DELETE CASCADE,

                FOREIGN KEY (concept_id)
                    REFERENCES concepts(id)
                    ON DELETE CASCADE,

                UNIQUE(username, concept_id)
            )
            """
        )

        # ========================================================
        # 10. LEARNER SKILL STATE
        # ========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS learner_skill_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT NOT NULL,

                skill_key TEXT NOT NULL,

                estimate REAL DEFAULT 0.0,

                confidence REAL DEFAULT 0.0,

                evidence_count INTEGER DEFAULT 0,

                recent_accuracy REAL,

                trend TEXT DEFAULT 'unknown',

                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (username)
                    REFERENCES users(username)
                    ON DELETE CASCADE,

                UNIQUE(username, skill_key)
            )
            """
        )

        # ========================================================
        # 11. LEARNER ERROR PATTERNS
        # ========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS learner_error_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT NOT NULL,

                concept_id INTEGER,

                pattern_key TEXT NOT NULL,

                category TEXT NOT NULL,

                description TEXT NOT NULL,

                occurrences INTEGER DEFAULT 1,

                confidence REAL DEFAULT 0.0,

                status TEXT DEFAULT 'suspected',

                first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (username)
                    REFERENCES users(username)
                    ON DELETE CASCADE,

                FOREIGN KEY (concept_id)
                    REFERENCES concepts(id)
                    ON DELETE SET NULL,

                UNIQUE(username, pattern_key)
            )
            """
        )

        # ========================================================
        # 12. PROFILE SUMMARY VERSIONS
        # ========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS profile_summary_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT NOT NULL,

                summary_data TEXT NOT NULL,

                evidence_count INTEGER DEFAULT 0,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (username)
                    REFERENCES users(username)
                    ON DELETE CASCADE
            )
            """
        )

        # ========================================================
        # 13. RETEST TARGETS
        # ========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS retest_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT NOT NULL,

                concept_id INTEGER,

                error_pattern_id INTEGER,

                reason TEXT NOT NULL,

                priority REAL DEFAULT 0.5,

                status TEXT DEFAULT 'pending',

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                completed_at TIMESTAMP,

                FOREIGN KEY (username)
                    REFERENCES users(username)
                    ON DELETE CASCADE,

                FOREIGN KEY (concept_id)
                    REFERENCES concepts(id)
                    ON DELETE SET NULL,

                FOREIGN KEY (error_pattern_id)
                    REFERENCES learner_error_patterns(id)
                    ON DELETE SET NULL
            )
            """
        )

        # ========================================================
        # INDEXES
        # ========================================================

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_personalization_user
            ON user_personalization_profiles(username)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_concepts_graph
            ON concepts(graph_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_questions_concept
            ON questions(concept_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_evidence_user
            ON quiz_evidence(username)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_web_quiz_results_user
            ON web_quiz_results(username, created_at DESC)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_web_lecture_progress_user
            ON web_lecture_progress(username, started_at DESC)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_evidence_concept
            ON quiz_evidence(concept_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_errors_user
            ON learner_error_patterns(username)
            """
        )

        conn.commit()

    finally:
        conn.close()


# ============================================================
# USER HELPERS
# ============================================================

def create_user(
    username: str,
    name: str,
    password_hash: str,
    full_profile: str = "",
) -> int:
    """
    Create a new authenticated user.

    password_hash must already be securely hashed by auth_service.
    """

    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO users (
                username,
                name,
                password_hash,
                full_profile,
                onboarding_complete
            )
            VALUES (?, ?, ?, ?, 0)
            """,
            (
                username,
                name,
                password_hash,
                full_profile,
            ),
        )

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def save_user(
    username: str,
    name: str,
    full_profile: str,
) -> None:
    """
    Legacy helper for older CLI code.

    New web signups must use create_user(), which stores password_hash.
    """

    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO users (
                username,
                name,
                full_profile,
                onboarding_complete
            )
            VALUES (?, ?, ?, 0)
            """,
            (
                username,
                name,
                full_profile,
            ),
        )

        conn.commit()

    finally:
        conn.close()


def update_user_profile(
    username: str,
    name: str,
    full_profile: str,
) -> None:
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE users
            SET
                name = ?,
                full_profile = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
            """,
            (
                name,
                full_profile,
                username,
            ),
        )

        conn.commit()

    finally:
        conn.close()


def user_exists(username: str) -> bool:
    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT 1
            FROM users
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

        return row is not None

    finally:
        conn.close()


def load_user(username: str) -> sqlite3.Row | None:
    """
    Internal database read.

    It includes password_hash because auth_service needs it to verify
    passwords. Never expose password_hash through API responses.
    """

    conn = get_connection()

    try:
        return conn.execute(
            """
            SELECT
                id,
                username,
                name,
                password_hash,
                full_profile,
                onboarding_complete,
                created_at,
                updated_at
            FROM users
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

    finally:
        conn.close()


def update_saved_explore_interest(
    username: str,
    topic: str,
    subject: str,
    status: str,
) -> list[dict[str, str]]:
    """Persist one saved/later Explore topic in the user's profile JSON."""
    if status not in {"saved", "later", "remove"}:
        raise ValueError("Interest status must be saved, later, or remove.")

    conn = get_connection()

    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            """
            SELECT name, full_profile
            FROM users
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

        if row is None:
            raise ValueError("User account was not found.")

        full_profile = row["full_profile"] or ""
        if full_profile.strip():
            profile_data = json.loads(full_profile)
            if not isinstance(profile_data, dict):
                raise ValueError("Saved user profile must be a JSON object.")
        else:
            profile_data = {
                "username": username,
                "name": row["name"],
            }

        saved_interests = profile_data.get("saved_interests", [])
        if not isinstance(saved_interests, list):
            raise ValueError("Saved profile interests must be a list.")

        normalized_topic = topic.strip()
        normalized_subject = subject.strip()
        topic_key = normalized_topic.casefold()
        subject_key = normalized_subject.casefold()

        saved_interests = [
            item
            for item in saved_interests
            if not (
                isinstance(item, dict)
                and str(item.get("topic", "")).strip().casefold()
                == topic_key
                and str(item.get("subject", "")).strip().casefold()
                == subject_key
            )
        ]

        if status != "remove":
            saved_interests.append(
                {
                    "topic": normalized_topic,
                    "subject": normalized_subject,
                    "status": status,
                }
            )

        profile_data["saved_interests"] = saved_interests
        conn.execute(
            """
            UPDATE users
            SET full_profile = ?, updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
            """,
            (
                json.dumps(profile_data, ensure_ascii=False),
                username,
            ),
        )
        conn.commit()
        return saved_interests

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def mark_onboarding_complete(username: str) -> None:
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE users
            SET
                onboarding_complete = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
            """,
            (username,),
        )

        conn.commit()

    finally:
        conn.close()


# ============================================================
# PERSONALIZATION PROFILE HELPERS
# ============================================================

def save_personalization_profile(
    username: str,
    answers: dict[str, Any],
    extra_learning_info: str = "",
) -> None:
    """
    Save the student-provided personalization answers.

    This represents 'You told us', not learner-model evidence.
    """

    answers_json = json.dumps(answers)

    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO user_personalization_profiles (
                username,
                answers_json,
                extra_learning_info,
                updated_at
            )
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)

            ON CONFLICT(username)
            DO UPDATE SET
                answers_json = excluded.answers_json,
                extra_learning_info = excluded.extra_learning_info,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                username,
                answers_json,
                extra_learning_info,
            ),
        )

        conn.commit()

    finally:
        conn.close()


def load_personalization_profile(
    username: str,
) -> dict[str, Any] | None:
    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT
                username,
                answers_json,
                extra_learning_info,
                created_at,
                updated_at
            FROM user_personalization_profiles
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

        if row is None:
            return None

        return {
            "username": row["username"],
            "answers": json.loads(row["answers_json"]),
            "extra_learning_info": row["extra_learning_info"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    finally:
        conn.close()
# ============================================================
# QUIZ DATABASE HELPERS
# ============================================================


def create_quiz_session(
    username: str,
    topic: str,
    purpose: str,
    difficulty: str = "standard",
    graph_id: int | None = None,
) -> int:
    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO quiz_sessions (
                username,
                topic,
                graph_id,
                purpose,
                difficulty,
                question_count,
                completed
            )
            VALUES (?, ?, ?, ?, ?, 0, 0)
            """,
            (
                username,
                topic,
                graph_id,
                purpose,
                difficulty,
            ),
        )

        conn.commit()
        return int(cursor.lastrowid)

    finally:
        conn.close()


def update_quiz_question_count(
    session_id: int,
    question_count: int,
) -> None:
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE quiz_sessions
            SET question_count = ?
            WHERE id = ?
            """,
            (
                question_count,
                session_id,
            ),
        )

        conn.commit()

    finally:
        conn.close()


def mark_quiz_completed(
    session_id: int,
) -> None:
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE quiz_sessions
            SET
                completed = 1,
                completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (session_id,),
        )

        conn.commit()

    finally:
        conn.close()


def load_quiz_session(
    session_id: int,
    username: str,
) -> sqlite3.Row | None:
    conn = get_connection()

    try:
        return conn.execute(
            """
            SELECT
                id,
                username,
                topic,
                graph_id,
                purpose,
                difficulty,
                question_count,
                completed,
                created_at,
                completed_at
            FROM quiz_sessions
            WHERE id = ?
              AND username = ?
            """,
            (
                session_id,
                username,
            ),
        ).fetchone()

    finally:
        conn.close()


def load_quiz_questions(
    session_id: int,
) -> list[sqlite3.Row]:
    conn = get_connection()

    try:
        return conn.execute(
            """
            SELECT
                q.id,
                q.question_key,
                q.question_text,
                q.question_type,
                q.cognitive_skill,
                q.difficulty,
                q.answer_format,
                q.expected_answer,
                q.explanation,
                q.possible_error_types,
                q.prerequisite_concepts,
                q.metadata,
                q.concept_id
            FROM questions AS q
            INNER JOIN concepts AS c
                ON c.id = q.concept_id
            INNER JOIN knowledge_graphs AS g
                ON g.id = q.graph_id
            INNER JOIN quiz_sessions AS s
                ON s.graph_id = g.id
            WHERE s.id = ?
            ORDER BY q.id ASC
            """,
            (session_id,),
        ).fetchall()

    finally:
        conn.close()


def save_quiz_evidence(
    username: str,
    session_id: int,
    question_id: int,
    concept_id: int,
    result: str,
    student_answer: str,
    correct_answer: str,
    question_type: str,
    cognitive_skill: str,
    difficulty: str,
    error_category: str | None = None,
    diagnosis_confidence: float | None = None,
    used_hint: bool = False,
    response_time_seconds: float | None = None,
    evaluator_notes: str | None = None,
) -> int:
    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO quiz_evidence (
                username,
                session_id,
                question_id,
                concept_id,
                result,
                student_answer,
                correct_answer,
                question_type,
                cognitive_skill,
                difficulty,
                error_category,
                diagnosis_confidence,
                used_hint,
                response_time_seconds,
                evaluator_notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                session_id,
                question_id,
                concept_id,
                result,
                student_answer,
                correct_answer,
                question_type,
                cognitive_skill,
                difficulty,
                error_category,
                diagnosis_confidence,
                int(used_hint),
                response_time_seconds,
                evaluator_notes,
            ),
        )

        conn.commit()
        return int(cursor.lastrowid)

    finally:
        conn.close()


def load_quiz_history(
    username: str,
    limit: int = 20,
) -> list[sqlite3.Row]:
    conn = get_connection()

    try:
        return conn.execute(
            """
            SELECT
                s.id,
                s.topic,
                s.purpose,
                s.difficulty,
                s.question_count,
                s.completed,
                s.created_at,
                s.completed_at,
                COUNT(e.id) AS answered_count,
                SUM(
                    CASE
                        WHEN e.result = 'correct'
                        THEN 1
                        ELSE 0
                    END
                ) AS correct_count
            FROM quiz_sessions AS s
            LEFT JOIN quiz_evidence AS e
                ON e.session_id = s.id
            WHERE s.username = ?
            GROUP BY s.id
            ORDER BY s.created_at DESC
            LIMIT ?
            """,
            (
                username,
                limit,
            ),
        ).fetchall()

    finally:
        conn.close()


def save_web_quiz_result(
    username: str,
    quiz_id: str,
    topic: str,
    score: int,
    correct_count: int,
    total_questions: int,
    feedback: str = "",
    next_step: str = "",
) -> None:
    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO web_quiz_results (
                username,
                quiz_id,
                topic,
                score,
                correct_count,
                total_questions,
                feedback,
                next_step
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(quiz_id)
            DO UPDATE SET
                score = excluded.score,
                correct_count = excluded.correct_count,
                total_questions = excluded.total_questions,
                feedback = excluded.feedback,
                next_step = excluded.next_step
            """,
            (
                username,
                quiz_id,
                topic,
                score,
                correct_count,
                total_questions,
                feedback,
                next_step,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def load_web_quiz_results(
    username: str,
) -> list[sqlite3.Row]:
    conn = get_connection()

    try:
        return conn.execute(
            """
            SELECT
                id,
                username,
                quiz_id,
                topic,
                score,
                correct_count,
                total_questions,
                feedback,
                next_step,
                created_at
            FROM web_quiz_results
            WHERE username = ?
            ORDER BY created_at DESC, id DESC
            """,
            (username,),
        ).fetchall()
    finally:
        conn.close()


def migrate_legacy_dashboard_results(
    legacy_file: Path | None = None,
) -> int:
    path = legacy_file or BASE_DIR / "dashboard_quiz_results.json"

    if not path.exists():
        return 0

    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Legacy dashboard results must be a JSON list.")

    conn = get_connection()
    imported_count = 0
    skipped_count = 0

    try:
        for record in records:
            if not isinstance(record, dict):
                raise ValueError("Legacy dashboard result entry is invalid.")

            username = record.get("username")
            quiz_id = record.get("quiz_id")
            topic = record.get("topic")
            score = record.get("score")
            correct_count = record.get("correct")
            total_questions = record.get("total")
            next_step = record.get("next_step", "")
            created_at = record.get("created_at")

            if (
                not isinstance(username, str)
                or not username.strip()
                or not isinstance(quiz_id, str)
                or not quiz_id.strip()
                or not isinstance(topic, str)
                or not topic.strip()
                or not isinstance(score, int)
                or not 0 <= score <= 100
                or not isinstance(correct_count, int)
                or not isinstance(total_questions, int)
                or total_questions < 0
                or not isinstance(next_step, str)
                or not isinstance(created_at, str)
            ):
                raise ValueError("Legacy dashboard result fields are invalid.")

            parsed_created_at = datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            )
            if parsed_created_at.tzinfo is not None:
                parsed_created_at = parsed_created_at.astimezone(
                    timezone.utc
                ).replace(tzinfo=None)
            created_at = parsed_created_at.strftime("%Y-%m-%d %H:%M:%S")

            user_exists = conn.execute(
                "SELECT 1 FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            if user_exists is None:
                skipped_count += 1
                continue

            cursor = conn.execute(
                """
                INSERT INTO web_quiz_results (
                    username,
                    quiz_id,
                    topic,
                    score,
                    correct_count,
                    total_questions,
                    feedback,
                    next_step,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, '', ?, ?)
                ON CONFLICT(quiz_id) DO NOTHING
                """,
                (
                    username,
                    quiz_id,
                    topic,
                    score,
                    correct_count,
                    total_questions,
                    next_step,
                    created_at,
                ),
            )
            imported_count += cursor.rowcount

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    if skipped_count:
        print(
            "Skipped "
            f"{skipped_count} legacy quiz result(s) because their users "
            "do not exist in the database."
        )

    return imported_count


def save_web_lecture_started(
    username: str,
    session_id: str,
    topic: str,
) -> None:
    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO web_lecture_progress (
                username,
                session_id,
                topic
            )
            VALUES (?, ?, ?)
            ON CONFLICT(session_id) DO NOTHING
            """,
            (username, session_id, topic),
        )
        conn.commit()
    finally:
        conn.close()


def mark_web_lecture_completed(
    username: str,
    session_id: str,
) -> bool:
    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            UPDATE web_lecture_progress
            SET completed_at = COALESCE(
                completed_at,
                CURRENT_TIMESTAMP
            )
            WHERE username = ?
              AND session_id = ?
            """,
            (username, session_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def load_web_lecture_progress(
    username: str,
) -> dict[str, int]:
    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS lectures_started,
                COUNT(DISTINCT topic) AS topics_studied,
                SUM(
                    CASE
                        WHEN completed_at IS NOT NULL THEN 1
                        ELSE 0
                    END
                ) AS lectures_completed
            FROM web_lecture_progress
            WHERE username = ?
            """,
            (username,),
        ).fetchone()
        return {
            "lectures_started": row["lectures_started"] or 0,
            "lectures_completed": row["lectures_completed"] or 0,
            "topics_studied": row["topics_studied"] or 0,
        }
    finally:
        conn.close()


def load_web_lecture_topics(
    username: str,
) -> list[sqlite3.Row]:
    conn = get_connection()

    try:
        return conn.execute(
            """
            SELECT DISTINCT topic
            FROM web_lecture_progress
            WHERE username = ?
            """,
            (username,),
        ).fetchall()
    finally:
        conn.close()