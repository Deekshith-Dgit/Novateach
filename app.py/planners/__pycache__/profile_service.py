import time

from modeles.user_profile import UserProfile
from services.ai_service import generate_ai_response


# ============================================================
# QUESTION HELPER
# ============================================================

def ask_question(question_text, options, progress=None):
    """
    Ask one onboarding question and return the selected option.
    """

    if progress is not None:
        print(f"\n📍 Progress: {progress}/6")

    print(f"\n{question_text}")

    for key, value in options.items():
        print(f"   {key}. {value}")

    while True:
        choice = input("\n➤ Your choice (A/B/C/D): ").strip().upper()

        if choice in options:
            return choice

        print("❌ Invalid choice. Please enter A, B, C, or D.")


# ============================================================
# CREATE PROFILE / ONBOARDING
# ============================================================

def create_profile():
    """
    Create a learner profile using 6 teaching-focused questions.

    The goal is NOT to diagnose the learner.

    The goal is to determine:
        - How to introduce concepts
        - How to explain difficult ideas
        - What creates difficulty
        - How to improve retention
        - How to control lesson depth
        - How to handle mistakes
    """

    print("\n" + "=" * 60)
    print("🚀 WELCOME TO NOVATEACH AI".center(60))
    print("=" * 60)

    name = input("\n👋 What's your name? ").strip()

    print(f"\nNice to meet you, {name}.")
    print(
        "I'll ask 6 quick questions so Novateach can understand "
        "how to teach you better."
    )

    time.sleep(0.8)

    # ========================================================
    # Q1 — CONCEPT INTRODUCTION
    # ========================================================

    q1 = ask_question(
        "Q1. When you meet a completely new concept, what usually "
        "helps you understand it fastest?",
        {
            "A": "A clear diagram or visual",
            "B": "A real-life example or analogy",
            "C": "A simple step-by-step explanation",
            "D": "Understanding the big picture and why it matters",
        },
        progress=1,
    )

    # ========================================================
    # Q2 — CONFUSION SUPPORT
    # ========================================================

    q2 = ask_question(
        "Q2. When you don't understand something, what usually "
        "helps you get it?",
        {
            "A": "Explain it again using simpler words",
            "B": "Show me a different example or analogy",
            "C": "Break it into smaller steps",
            "D": "Connect it to something I already understand",
        },
        progress=2,
    )

    # ========================================================
    # Q3 — DIFFICULTY PATTERN
    # ========================================================

    q3 = ask_question(
        "Q3. Which type of learning material usually causes you "
        "the most difficulty?",
        {
            "A": "Formulas, calculations, or mathematical steps",
            "B": "Abstract ideas and explanations",
            "C": "Many new terms, facts, or definitions",
            "D": "Problems requiring several steps or concepts together",
        },
        progress=3,
    )

    # ========================================================
    # Q4 — RETENTION
    # ========================================================

    q4 = ask_question(
        "Q4. What usually happens when you learn something but "
        "don't remember it later?",
        {
            "A": "I understood it at first but forget it with time",
            "B": "I remember the idea but confuse it with similar ideas",
            "C": "I remember it when I see it but struggle to recall it myself",
            "D": "I remember the information but forget how to use it",
        },
        progress=4,
    )

    # ========================================================
    # Q5 — PACING / DEPTH
    # ========================================================

    q5 = ask_question(
        "Q5. How should Novateach usually explain a new topic?",
        {
            "A": "Short and focused — get to the main idea quickly",
            "B": "Balanced — enough explanation without unnecessary detail",
            "C": "Detailed — explain the reasoning and connections deeply",
            "D": "Adapt the depth depending on how difficult the concept is",
        },
        progress=5,
    )

    # ========================================================
    # Q6 — ERROR RECOVERY
    # ========================================================

    q6 = ask_question(
        "Q6. After you make a mistake, what would help you learn "
        "from it most?",
        {
            "A": "Explain exactly why my answer was wrong",
            "B": "Show me a similar example",
            "C": "Give me a hint and let me try again",
            "D": "Explain the concept differently and then let me retry",
        },
        progress=6,
    )

    # ========================================================
    # OPEN-ENDED INPUT
    # ========================================================

    print("\n📝 One final thing.")

    print(
        "Tell Novateach anything else that could help it "
        "teach you better."
    )

    print(
        "For example: what makes you understand something quickly, "
        "what makes you forget, or anything you want your AI teacher "
        "to know."
    )

    personal_info = input("\n➤ Your response: ").strip()

    # ========================================================
    # DETERMINISTIC INTERPRETATION
    # ========================================================

    understanding_map = {
        "A": "Visual-first",
        "B": "Example-first",
        "C": "Step-by-step",
        "D": "Big-picture-first",
    }

    support_map = {
        "A": "Simplify the explanation",
        "B": "Use a different example or analogy",
        "C": "Break the concept into smaller steps",
        "D": "Connect the concept to prior knowledge",
    }

    difficulty_map = {
        "A": "Formulas and calculations",
        "B": "Abstract concepts",
        "C": "Terminology and factual information",
        "D": "Multi-step reasoning and application",
    }

    retention_map = {
        "A": "Needs reinforcement over time",
        "B": "Needs stronger distinction between similar concepts",
        "C": "Needs active retrieval practice",
        "D": "Needs more application and transfer practice",
    }

    pace_map = {
        "A": "Short and focused",
        "B": "Balanced",
        "C": "Detailed and deep",
        "D": "Adaptive depth based on concept difficulty",
    }

    recovery_map = {
        "A": "Explicit error explanation",
        "B": "Similar worked example",
        "C": "Hint followed by retry",
        "D": "Alternative explanation followed by retry",
    }

    understanding_strategy = understanding_map[q1]
    support_strategy = support_map[q2]
    difficulty_trigger = difficulty_map[q3]
    retention_pattern = retention_map[q4]
    pace_preference = pace_map[q5]
    recovery_strategy = recovery_map[q6]

    # ========================================================
    # BACKWARD COMPATIBILITY
    # ========================================================

    learning_style = understanding_strategy
    confusion_pattern = support_strategy

    learning_goal = (
        "Deep understanding and long-term retention"
    )

    confidence_level = "Not assessed"

    interest_area = None

    # ========================================================
    # RAW ANSWERS
    # ========================================================

    onboarding_answers = {
        "q1_concept_introduction": q1,
        "q2_confusion_support": q2,
        "q3_difficulty_pattern": q3,
        "q4_retention_pattern": q4,
        "q5_pacing_depth": q5,
        "q6_error_recovery": q6,
    }

    # ========================================================
    # AI TEACHING PROFILE
    # ========================================================

    snapshot_prompt = f"""
You are Novateach AI's personalization engine.

Your job is NOT to diagnose the learner and NOT to assign a fixed
"learning style".

Your job is to determine:

"How should Novateach teach THIS learner so they understand concepts
deeply, understand them efficiently, and retain them?"

The learner has answered only 6 onboarding questions.

Therefore:
- Treat every conclusion as a preference/hypothesis.
- Never claim that a preference is an objective cognitive trait.
- Never infer intelligence.
- Never infer mastery.
- Never infer academic ability.
- Never assign Basic / Intermediate / Advanced level.
- Actual difficulty level must later come from quiz performance.

============================================================
LEARNER
============================================================

Name:
{name}

Personal Note:
{personal_info or "None"}

============================================================
OBSERVED ONBOARDING SIGNALS
============================================================

Concept Introduction:
{understanding_strategy}

Confusion Support:
{support_strategy}

Main Difficulty:
{difficulty_trigger}

Retention Pattern:
{retention_pattern}

Preferred Pace / Depth:
{pace_preference}

Error Recovery:
{recovery_strategy}

============================================================
CREATE A TEACHING CONFIGURATION
============================================================

The output will be consumed by:

- Lecture Generator
- Visual Director
- Quiz Generator
- Doubt Solver
- Revision System
- Future Adaptive Learning Engine

Do NOT write a generic learner description.

Write concrete instructions that another AI can directly follow.

============================================================
OUTPUT
============================================================

[TEACHING CONFIGURATION]

INTRODUCTION METHOD
Primary:
Secondary:
Start With:
Avoid Starting With:

EXPLANATION METHOD
Structure:
Language:
Example Frequency:
Connection To Prior Knowledge:

VISUAL STRATEGY
Use Visuals:
Preferred Visual Purpose:
When To Use Visuals:

PACING
Initial Chunk Size:
Explanation Depth:
When To Expand:
When To Simplify:

MEMORY & RETENTION
Retrieval Practice:
Spaced Reinforcement:
Application Practice:
Memory Technique:

ERROR RECOVERY
First Response:
Second Response:
Retry Strategy:

QUIZ STRATEGY
Conceptual Questions:
Application Questions:
Difficulty Progression:
Mistake Analysis:

DOUBT SOLVING
First Step:
Explanation Style:
Follow-up Check:

============================================================
ADAPTIVE RULES
============================================================

Write exactly 8 rules.

Rules must follow this format:

IF [observable learning situation]
THEN [specific teaching action]

Example:

IF the learner struggles with a formula
THEN explain the meaning of each variable before asking another
calculation question.

Do NOT create rules based on personality.

============================================================
WHAT WE DO NOT KNOW YET
============================================================

Write exactly 4 things that cannot be determined from onboarding
and must be learned from future behaviour.

Examples:
- Actual topic mastery
- True retention over time
- Ability to transfer knowledge
- Optimal difficulty level

============================================================
PROFILE CONFIDENCE
============================================================

Overall Confidence:
Low / Medium / High

Reason:

============================================================
IMPORTANT
============================================================

This profile is an initial hypothesis based only on onboarding
responses.

It MUST evolve using:

- Quiz performance
- Question-level mistakes
- Retry performance
- Doubt history
- Learner feedback
- Retention checks
- Topic-level mastery
- Learning behaviour

Never treat onboarding as permanent truth.

Keep the output concise and highly actionable.

"""

    print("\n🧠 Creating your personalized teaching profile...\n")

    learning_snapshot = generate_ai_response(
        snapshot_prompt
    )

    # ========================================================
    # CREATE USER PROFILE
    # ========================================================

    profile = UserProfile(
        name=name,

        # Existing fields
        learning_style=learning_style,
        confusion_pattern=confusion_pattern,
        difficulty_trigger=difficulty_trigger,
        learning_goal=learning_goal,
        confidence_level=confidence_level,
        personal_info=personal_info,
        learning_snapshot=learning_snapshot,
        interest_area=interest_area,

        # New personalization fields
        understanding_strategy=understanding_strategy,
        support_strategy=support_strategy,
        retention_pattern=retention_pattern,
        pace_preference=pace_preference,
        teaching_strategy=learning_snapshot,
        onboarding_answers=onboarding_answers,
    )

    # Recovery strategy is stored separately so older versions
    # of UserProfile remain compatible.
    profile.recovery_strategy = recovery_strategy

    return profile


# ============================================================
# PROFILE SERVICE
# ============================================================

class ProfileService:
    """
    Central interface for accessing learner personalization.
    """

    def __init__(self, profile):
        if profile is None:
            raise ValueError("Profile cannot be None.")

        self.profile = profile

    # ========================================================
    # BASIC PROFILE
    # ========================================================

    def get_profile(self):
        return self.profile

    # ========================================================
    # TEACHING STRATEGY
    # ========================================================

    def get_teaching_strategy(self):
        """
        Return the generated teaching strategy.
        """

        strategy = getattr(
            self.profile,
            "teaching_strategy",
            None
        )

        if strategy:
            return strategy

        snapshot = getattr(
            self.profile,
            "learning_snapshot",
            None
        )

        return snapshot or ""

    # ========================================================
    # TEACHING PREFERENCES
    # ========================================================

    def get_teaching_preferences(self):
        """
        Return structured personalization signals.
        """

        return {
            "understanding_strategy": getattr(
                self.profile,
                "understanding_strategy",
                None
            ),

            "support_strategy": getattr(
                self.profile,
                "support_strategy",
                None
            ),

            "difficulty_trigger": getattr(
                self.profile,
                "difficulty_trigger",
                None
            ),

            "retention_pattern": getattr(
                self.profile,
                "retention_pattern",
                None
            ),

            "pace_preference": getattr(
                self.profile,
                "pace_preference",
                None
            ),

            "recovery_strategy": getattr(
                self.profile,
                "recovery_strategy",
                None
            ),
        }

    # ========================================================
    # LECTURE CONTEXT
    # ========================================================

    def get_lecture_context(self):
        """
        Return the personalization context required by
        the lecture generation system.
        """

        return {
            "learner_name": getattr(
                self.profile,
                "name",
                None
            ),

            "learning_goal": getattr(
                self.profile,
                "learning_goal",
                None
            ),

            "understanding_strategy": getattr(
                self.profile,
                "understanding_strategy",
                None
            ),

            "support_strategy": getattr(
                self.profile,
                "support_strategy",
                None
            ),

            "difficulty_trigger": getattr(
                self.profile,
                "difficulty_trigger",
                None
            ),

            "retention_pattern": getattr(
                self.profile,
                "retention_pattern",
                None
            ),

            "pace_preference": getattr(
                self.profile,
                "pace_preference",
                None
            ),

            "recovery_strategy": getattr(
                self.profile,
                "recovery_strategy",
                None
            ),

            "teaching_strategy": self.get_teaching_strategy(),
        }

    # ========================================================
    # QUIZ CONTEXT
    # ========================================================

    def get_quiz_context(self):
        """
        Return personalization information for quiz generation.
        """

        return {
            "learning_goal": getattr(
                self.profile,
                "learning_goal",
                None
            ),

            "difficulty_trigger": getattr(
                self.profile,
                "difficulty_trigger",
                None
            ),

            "retention_pattern": getattr(
                self.profile,
                "retention_pattern",
                None
            ),

            "recovery_strategy": getattr(
                self.profile,
                "recovery_strategy",
                None
            ),

            "teaching_strategy": self.get_teaching_strategy(),
        }

    # ========================================================
    # DOUBT CONTEXT
    # ========================================================

    def get_doubt_context(self):
        """
        Return personalization information for doubt solving.
        """

        return {
            "understanding_strategy": getattr(
                self.profile,
                "understanding_strategy",
                None
            ),

            "support_strategy": getattr(
                self.profile,
                "support_strategy",
                None
            ),

            "difficulty_trigger": getattr(
                self.profile,
                "difficulty_trigger",
                None
            ),

            "pace_preference": getattr(
                self.profile,
                "pace_preference",
                None
            ),

            "recovery_strategy": getattr(
                self.profile,
                "recovery_strategy",
                None
            ),

            "teaching_strategy": self.get_teaching_strategy(),
        }

    # ========================================================
    # VISUAL CONTEXT
    # ========================================================

    def get_visual_context(self):
        """
        Return personalization information for visual generation.
        """

        return {
            "understanding_strategy": getattr(
                self.profile,
                "understanding_strategy",
                None
            ),

            "difficulty_trigger": getattr(
                self.profile,
                "difficulty_trigger",
                None
            ),

            "pace_preference": getattr(
                self.profile,
                "pace_preference",
                None
            ),

            "teaching_strategy": self.get_teaching_strategy(),
        }

    # ========================================================
    # RETENTION CONTEXT
    # ========================================================

    def get_retention_context(self):
        """
        Return information relevant to memory and retention.
        """

        return {
            "retention_pattern": getattr(
                self.profile,
                "retention_pattern",
                None
            ),

            "learning_goal": getattr(
                self.profile,
                "learning_goal",
                None
            ),

            "teaching_strategy": self.get_teaching_strategy(),
        }

    # ========================================================
    # COMPLETE AI CONTEXT
    # ========================================================

    def get_ai_context(self):
        """
        Return the complete personalization context.

        This can be passed to AI-powered services.
        """

        return {
            "learner_name": getattr(
                self.profile,
                "name",
                None
            ),

            "learning_goal": getattr(
                self.profile,
                "learning_goal",
                None
            ),

            "understanding_strategy": getattr(
                self.profile,
                "understanding_strategy",
                None
            ),

            "support_strategy": getattr(
                self.profile,
                "support_strategy",
                None
            ),

            "difficulty_trigger": getattr(
                self.profile,
                "difficulty_trigger",
                None
            ),

            "retention_pattern": getattr(
                self.profile,
                "retention_pattern",
                None
            ),

            "pace_preference": getattr(
                self.profile,
                "pace_preference",
                None
            ),

            "recovery_strategy": getattr(
                self.profile,
                "recovery_strategy",
                None
            ),

            "teaching_strategy": self.get_teaching_strategy(),
        }

    # ========================================================
    # SUMMARY
    # ========================================================

    def get_summary(self):
        """
        Return the profile's human-readable summary.
        """

        if hasattr(self.profile, "get_summary"):
            return self.profile.get_summary()

        return str(self.profile)

    # ========================================================
    # LEARNING EVENT
    # ========================================================

    def record_learning_event(self, event):
        """
        Store a learning event for future adaptive learning.

        Example:

        {
            "type": "quiz_result",
            "topic": "ohms_law",
            "score": 0.8
        }
        """

        if not isinstance(event, dict):
            raise TypeError(
                "Learning event must be a dictionary."
            )

        if not hasattr(
            self.profile,
            "learning_history"
        ):
            self.profile.learning_history = []

        self.profile.learning_history.append(event)

    # ========================================================
    # FEEDBACK
    # ========================================================

    def record_feedback(self, feedback):
        """
        Store learner feedback for future profile updates.
        """

        if not hasattr(
            self.profile,
            "feedback_history"
        ):
            self.profile.feedback_history = []

        self.profile.feedback_history.append(feedback)


# ============================================================
# HELPER
# ============================================================

def create_profile_service(profile):
    """
    Convenience function for creating ProfileService.
    """

    return ProfileService(profile)
  