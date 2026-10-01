import { useCallback, useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const personalizationQuestions = [
  {
    key: "understanding_strategy",
    label: "When you are learning something new, what helps you understand it best?",
    options: [
      "A simple explanation",
      "Examples or analogies",
      "Visuals or diagrams",
      "Trying problems myself",
    ],
  },
  {
    key: "support_strategy",
    label: "When you get confused, what kind of help do you usually want?",
    options: [
      "Explain it more simply",
      "Give me an example",
      "Break it into smaller steps",
      "Find exactly where I got confused",
    ],
  },
  {
    key: "difficulty_trigger",
    label: "What usually makes a topic difficult for you?",
    options: [
      "Too much information at once",
      "Missing the basic concepts",
      "I understand theory but struggle to apply it",
      "I forget what I learned",
    ],
  },
  {
    key: "teaching_strategy",
    label: "Which learning flow feels most natural to you?",
    options: [
      "Concept → Example → Practice",
      "Example → Explanation → Practice",
      "Visual → Explanation → Practice",
      "Problem → Concept → Practice",
    ],
  },
  {
    key: "retention_pattern",
    label: "What best describes how you remember things?",
    options: [
      "I remember the main idea but forget details",
      "I remember it better after practicing",
      "I need revision to remember it",
      "I usually remember it well",
    ],
  },
  {
    key: "pace_preference",
    label: "How would you like Novateach to pace your learning?",
    options: [
      "Slow and detailed",
      "Moderate",
      "Fast",
      "Adaptive — slow down when I struggle",
    ],
  },
];

const learningInsights = [
  "Understanding comes before speed.",
  "Strong learning is built from connections, not isolated facts.",
  "A difficult idea often becomes easier when you find the idea underneath it.",
  "Getting something wrong can reveal exactly what needs attention.",
  "You do not need to understand everything at once.",
  "Good questions are often the beginning of good understanding.",
];

const interestOptions = [
  "Mathematics",
  "Physics",
  "Computer Science",
  "Psychology",
  "Biology",
  "Economics",
];

const exploreSubjects = [
  {
    id: "mathematics",
    name: "Mathematics",
    description: "Patterns, structures, logic and quantitative thinking.",
    topics: [
      {
        name: "Differentiation",
        description: "Understand rates of change and derivatives.",
      },
      {
        name: "Integration",
        description: "Explore accumulation, area and antiderivatives.",
      },
      {
        name: "Probability",
        description: "Reason about uncertainty and chance.",
      },
      {
        name: "Statistics",
        description: "Turn data into meaningful conclusions.",
      },
    ],
  },
  {
    id: "physics",
    name: "Physics",
    description: "Understand how the physical world behaves.",
    topics: [
      {
        name: "Electric Fields",
        description: "Understand how charges influence space.",
      },
      {
        name: "Mechanics",
        description: "Explore motion, forces and energy.",
      },
      {
        name: "Waves",
        description: "Understand oscillations, sound and propagation.",
      },
    ],
  },
  {
    id: "computer-science",
    name: "Computer Science",
    description: "Build systems and learn how computation works.",
    topics: [
      {
        name: "Programming",
        description: "Turn ideas into working programs.",
      },
      {
        name: "Algorithms",
        description: "Learn how problems become solvable.",
      },
      {
        name: "Artificial Intelligence",
        description: "Understand how machines learn and reason.",
      },
    ],
  },
  {
    id: "psychology",
    name: "Psychology",
    description: "Understand people, behaviour and cognition.",
    topics: [
      {
        name: "Human Behaviour",
        description: "Explore why people think and act differently.",
      },
      {
        name: "Memory",
        description: "Understand how people learn and remember.",
      },
      {
        name: "Decision Making",
        description: "Explore how people make choices.",
      },
    ],
  },
  {
    id: "biology",
    name: "Biology",
    description: "Understand living systems from cells to ecosystems.",
    topics: [
      {
        name: "Cell Biology",
        description: "Explore the basic unit of life.",
      },
      {
        name: "Genetics",
        description: "Understand inheritance and variation.",
      },
      {
        name: "Ecology",
        description: "Understand relationships between organisms and environments.",
      },
    ],
  },
  {
    id: "economics",
    name: "Economics",
    description: "Understand decisions, incentives and systems.",
    topics: [
      {
        name: "Microeconomics",
        description: "Explore choices made by people and firms.",
      },
      {
        name: "Macroeconomics",
        description: "Understand economies at a larger scale.",
      },
      {
        name: "Game Theory",
        description: "Explore strategic decision making.",
      },
    ],
  },
];

function LectureContents({
  prerequisites = [],
  mainPages = [],
  currentPage,
  onPrerequisiteClick,
  onPageClick,
}) {
  return (
    <aside className="lecture-contents">
      <h2>Contents</h2>

      {prerequisites.length > 0 && (
        <section>
          <p className="contents-label">Prerequisites</p>

          {prerequisites.map((item) => (
            <button
              key={item.node_id}
              type="button"
              className={`contents-item prerequisite ${item.status || ""}`}
              onClick={() => onPrerequisiteClick(item)}
            >
              <span className="contents-number">{item.display_number}</span>
              <span>{item.title}</span>
            </button>
          ))}
        </section>
      )}

      <section>
        <p className="contents-label">Main topic</p>

        {mainPages.map((item) => {
          const pageNumber = item.display_number;
          const isCurrent = pageNumber === currentPage;
          const isAvailable = pageNumber <= currentPage;

          return (
            <button
              key={item.node_id}
              type="button"
              className={`contents-item ${isCurrent ? "current" : ""} ${!isAvailable ? "locked" : ""}`}
              disabled={!isAvailable}
              onClick={() => onPageClick(pageNumber)}
            >
              <span className="contents-number">{String(pageNumber).padStart(2, "0")}</span>
              <span>{item.title}</span>
            </button>
          );
        })}
      </section>
    </aside>
  );
}

function App() {
  const [started, setStarted] = useState(false);
  const [isEntering, setIsEntering] = useState(false);

  const [showAuth, setShowAuth] = useState(false);
  const [authMode, setAuthMode] = useState("login");

  const [username, setUsername] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");

  const [authLoading, setAuthLoading] = useState(false);
  const [authMessage, setAuthMessage] = useState("");
  const [authenticatedUser, setAuthenticatedUser] = useState(null);

  const [personalizationIntro, setPersonalizationIntro] = useState(false);
  const [personalizing, setPersonalizing] = useState(false);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [extraInfo, setExtraInfo] = useState("");
  const [savingPersonalization, setSavingPersonalization] = useState(false);
  const [personalizationMessage, setPersonalizationMessage] = useState("");

  const [currentView, setCurrentView] = useState("entry");

  const [topic, setTopic] = useState("");
  const [academicLevel, setAcademicLevel] = useState("");
  const [difficultyLevel, setDifficultyLevel] = useState("standard");

  const [learningStage, setLearningStage] = useState("input");
  const [topicResolution, setTopicResolution] = useState(null);
  const [learningError, setLearningError] = useState("");
  const [generating, setGenerating] = useState(false);

  const [lectureSession, setLectureSession] = useState(null);
  const [lecturePageNumber, setLecturePageNumber] = useState(1);
  const [currentLecturePage, setCurrentLecturePage] = useState(null);
  const [pageLoading, setPageLoading] = useState(false);
  const [lectureError, setLectureError] = useState("");
  const [quizMode, setQuizMode] = useState(false);

  const [selectedPrerequisite, setSelectedPrerequisite] = useState(null);
  const [prerequisiteLoading, setPrerequisiteLoading] = useState(false);

  const [selectedInterests, setSelectedInterests] = useState(() => {
    if (typeof window === "undefined") {
      return [];
    }

    try {
      const savedInterests = localStorage.getItem("novateach_explore_interests");
      if (!savedInterests) {
        return [];
      }

      const parsed = JSON.parse(savedInterests);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  });

  const [explorePersonalized, setExplorePersonalized] = useState(() => {
    if (typeof window === "undefined") {
      return false;
    }

    try {
      return Boolean(localStorage.getItem("novateach_explore_interests"));
    } catch {
      return false;
    }
  });

  const personalizedSubjects = useMemo(() => {
    if (!explorePersonalized) {
      return exploreSubjects;
    }

    return exploreSubjects.filter((subject) =>
      selectedInterests.includes(subject.name),
    );
  }, [explorePersonalized, selectedInterests]);

  function readResponse(response) {
    return response.json().catch(() => ({}));
  }

  function handleEnter() {
    if (isEntering) {
      return;
    }

    setIsEntering(true);
    setStarted(true);

    window.setTimeout(() => {
      setShowAuth(true);
      setCurrentView("auth");
      setIsEntering(false);
    }, 450);
  }

  function openLogin() {
    setAuthMode("login");
    setAuthMessage("");
    setPassword("");
  }

  function openSignup() {
    setAuthMode("signup");
    setAuthMessage("");
    setPassword("");
  }

  function openPersonalizationIntro() {
    setShowAuth(false);
    setPersonalizationIntro(true);
    setPersonalizing(false);
    setCurrentView("personalization-intro");
  }

  function startPersonalization() {
    setQuestionIndex(0);
    setAnswers({});
    setExtraInfo("");
    setPersonalizationMessage("");
    setPersonalizationIntro(false);
    setPersonalizing(true);
    setCurrentView("personalization");
  }

  async function handleLogin(event) {
    event.preventDefault();

    if (!username.trim()) {
      setAuthMessage("Please enter your username.");
      return;
    }

    if (!password) {
      setAuthMessage("Please enter your password.");
      return;
    }

    setAuthLoading(true);
    setAuthMessage("");

    try {
      const response = await fetch(`${API_BASE}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username.trim(),
          password,
        }),
      });

      const data = await readResponse(response);

      if (!response.ok || data.status === "error") {
        setAuthMessage(data.message || data.detail || "Unable to sign in.");
        return;
      }

      const user = {
        userId: data.user_id,
        username: data.username,
        name: data.name,
        onboardingComplete: Boolean(data.onboarding_complete),
      };

      setAuthenticatedUser(user);
      setShowAuth(false);
      setAuthMessage("");

      if (data.onboarding_complete) {
        setCurrentView("home");
        setLearningStage("input");
      } else {
        openPersonalizationIntro();
      }
    } catch (error) {
      console.error(error);
      setAuthMessage("Unable to connect to Novateach.");
    } finally {
      setAuthLoading(false);
    }
  }

  async function handleSignup(event) {
    event.preventDefault();

    if (!username.trim()) {
      setAuthMessage("Please enter a username.");
      return;
    }

    if (!name.trim()) {
      setAuthMessage("Please enter your name.");
      return;
    }

    if (password.length < 8) {
      setAuthMessage("Password must have at least 8 characters.");
      return;
    }

    setAuthLoading(true);
    setAuthMessage("");

    try {
      const response = await fetch(`${API_BASE}/api/auth/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username.trim(),
          name: name.trim(),
          password,
        }),
      });

      const data = await readResponse(response);

      if (!response.ok || data.status === "error") {
        setAuthMessage(data.message || data.detail || "Unable to create account.");
        return;
      }

      setAuthenticatedUser({
        userId: data.user_id,
        username: data.username,
        name: data.name,
        onboardingComplete: false,
      });
      setShowAuth(false);
      setAuthMessage("");
      openPersonalizationIntro();
    } catch (error) {
      console.error(error);
      setAuthMessage("Unable to connect to Novateach.");
    } finally {
      setAuthLoading(false);
    }
  }

  function handleOptionSelect(option) {
    const question = personalizationQuestions[questionIndex];

    setAnswers((previous) => ({
      ...previous,
      [question.key]: option,
    }));

    setPersonalizationMessage("");

    if (questionIndex < personalizationQuestions.length - 1) {
      setQuestionIndex((previous) => previous + 1);
    }
  }

  function handleBackQuestion() {
    if (questionIndex > 0 && !savingPersonalization) {
      setQuestionIndex((previous) => previous - 1);
    }
  }

  async function handleFinishPersonalization() {
    if (!authenticatedUser) {
      setPersonalizationMessage("Please sign in again.");
      return;
    }

    const missingQuestion = personalizationQuestions.find(
      (question) => !answers[question.key],
    );

    if (missingQuestion) {
      setPersonalizationMessage("Please answer every question.");
      return;
    }

    setSavingPersonalization(true);
    setPersonalizationMessage("");

    try {
      const response = await fetch(`${API_BASE}/api/profile/personalization`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: authenticatedUser.username,
          answers,
          extra_learning_info: extraInfo.trim(),
        }),
      });

      const data = await readResponse(response);

      if (!response.ok || data.status === "error") {
        setPersonalizationMessage(
          data.message || data.detail || "Could not save personalization.",
        );
        return;
      }

      setAuthenticatedUser((previous) => ({
        ...previous,
        onboardingComplete: true,
      }));

      setPersonalizing(false);
      setPersonalizationIntro(false);
      setCurrentView("home");
      setLearningStage("input");
    } catch (error) {
      console.error(error);
      setPersonalizationMessage("Unable to save personalization.");
    } finally {
      setSavingPersonalization(false);
    }
  }

  function resetLearningFlow() {
    setLearningStage("input");
    setTopicResolution(null);
    setLearningError("");
    setLectureSession(null);
    setCurrentLecturePage(null);
    setLecturePageNumber(1);
    setQuizMode(false);
    setSelectedPrerequisite(null);
    setCurrentView("home");
  }

  function handleSubjectSelect(subject) {
    setTopicResolution(null);
    setLearningStage("input");
    startProgressiveLecture(subject);
  }

  async function startProgressiveLecture(requestedSubject = "") {
    if (!authenticatedUser) {
      setLearningError("Please sign in before starting a lecture.");
      return;
    }

    if (!topic.trim()) {
      setLearningError("Please enter a topic.");
      return;
    }

    if (!academicLevel.trim()) {
      setLearningError("Please enter your academic level.");
      return;
    }

    setGenerating(true);
    setLearningError("");
    setLectureError("");
    setQuizMode(false);
    setLectureSession(null);
    setCurrentLecturePage(null);
    setLecturePageNumber(1);

    try {
      const response = await fetch(`${API_BASE}/api/lecture/start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: authenticatedUser.username,
          topic: topic.trim(),
          academic_level: academicLevel.trim(),
          difficulty: difficultyLevel,
          subject: requestedSubject,
          learner_profile: {},
        }),
      });

      const data = await readResponse(response);

      if (!response.ok) {
        throw new Error(data.detail || "Could not start the lecture.");
      }

      if (data.status === "ambiguous") {
        setTopicResolution(data.resolution);
        setLearningStage("subject");
        setCurrentView("home");
        return;
      }

      if (data.status === "invalid") {
        setLearningError(
          data.resolution?.reason || "This topic could not be resolved.",
        );
        setLearningStage("input");
        setCurrentView("home");
        return;
      }

      if (data.status !== "success") {
        throw new Error(data.message || "Lecture session was not created.");
      }

      const session = data.session;
      setLectureSession(session);
      setLearningStage("lecture");
      setCurrentView("lecture");

      await loadLecturePage(session.session_id, 1);
    } catch (error) {
      console.error(error);
      setLectureError(error.message);
      setLearningError(error.message);
      setCurrentView("home");
    } finally {
      setGenerating(false);
    }
  }

  async function loadLecturePage(sessionId, pageNumber) {
    setPageLoading(true);
    setLectureError("");

    try {
      const response = await fetch(
        `${API_BASE}/api/lecture/${sessionId}/page/${pageNumber}`,
      );

      const data = await readResponse(response);

      if (!response.ok) {
        throw new Error(data.detail || "Could not load lecture page.");
      }

      setLecturePageNumber(pageNumber);
      setCurrentLecturePage(data);

      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    } catch (error) {
      console.error(error);
      setLectureError(error.message);
    } finally {
      setPageLoading(false);
    }
  }

  const prefetchLecturePage = useCallback(
    async (pageNumber) => {
      if (!lectureSession) {
        return;
      }

      const totalPages = lectureSession.main_pages?.length || 0;

      if (pageNumber < 1 || pageNumber > totalPages) {
        return;
      }

      try {
        const response = await fetch(
          `${API_BASE}/api/lecture/${lectureSession.session_id}/prefetch`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              page_number: pageNumber,
            }),
          },
        );

        await readResponse(response);
      } catch (error) {
        console.warn("Prefetch request failed:", error);
      }
    },
    [lectureSession],
  );

  useEffect(() => {
    if (!lectureSession || !lecturePageNumber || lectureSession.session_type === "prerequisite") {
      return;
    }

    prefetchLecturePage(lecturePageNumber + 2);
  }, [lecturePageNumber, lectureSession, prefetchLecturePage]);

  async function continueLecture() {
    if (!lectureSession) {
      return;
    }

    const nextPage = lecturePageNumber + 1;
    const totalPages = lectureSession.main_pages?.length || 0;

    if (nextPage > totalPages) {
      setQuizMode(true);
      return;
    }

    await loadLecturePage(lectureSession.session_id, nextPage);
  }

  function handlePrerequisiteClick(item) {
    setSelectedPrerequisite(item);
  }

  async function startPrerequisite(prerequisiteNodeId) {
    if (!lectureSession) {
      return;
    }

    setPrerequisiteLoading(true);
    setLectureError("");

    try {
      const response = await fetch(
        `${API_BASE}/api/lecture/${lectureSession.session_id}/prerequisite/start`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prerequisite_node_id: prerequisiteNodeId,
          }),
        },
      );

      const data = await readResponse(response);

      if (!response.ok) {
        throw new Error(data.detail || "Could not start prerequisite.");
      }

      const childPages = data.session.pages || {};

      if (!childPages["1"] && !childPages[1]) {
        throw new Error(
          "Prerequisite session was created, but its first page is not ready.",
        );
      }

      setSelectedPrerequisite(null);
      setLectureSession(data.session);
      setLecturePageNumber(1);
      setCurrentLecturePage(null);
      setCurrentView("lecture");

      await loadLecturePage(data.session.session_id, 1);
    } catch (error) {
      setLectureError(error.message);
    } finally {
      setPrerequisiteLoading(false);
    }
  }

  async function skipPrerequisite() {
    if (!lectureSession || lectureSession.session_type !== "prerequisite") {
      return;
    }

    const parentSessionId = lectureSession.parent_session_id;
    const returnPage = lectureSession.return_page || 1;

    if (!parentSessionId) {
      setLectureError("Original lecture ID is missing.");
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/lecture/${parentSessionId}`);
      const data = await readResponse(response);

      if (!response.ok) {
        throw new Error(data.detail || "Could not return to the lecture.");
      }

      const parentSession = data.session;

      setLectureSession(parentSession);
      setLecturePageNumber(returnPage);
      setCurrentLecturePage(null);
      setSelectedPrerequisite(null);
      setCurrentView("lecture");

      await loadLecturePage(parentSessionId, returnPage);
    } catch (error) {
      console.error(error);
      setLectureError(error.message);
    }
  }

  async function continueWithOriginalLecture() {
    if (!lectureSession || lectureSession.session_type !== "prerequisite") {
      return;
    }

    const parentSessionId = lectureSession.parent_session_id;
    const returnPage = lectureSession.return_page || 1;

    try {
      const response = await fetch(`${API_BASE}/api/lecture/${parentSessionId}`);
      const data = await readResponse(response);

      if (!response.ok) {
        throw new Error(data.detail || "Could not return to the lecture.");
      }

      setLectureSession(data.session);
      setLecturePageNumber(returnPage);
      setCurrentLecturePage(null);
      setCurrentView("lecture");

      await loadLecturePage(parentSessionId, returnPage);
    } catch (error) {
      setLectureError(error.message);
    }
  }

  function handleTopicSubmit(event) {
    event.preventDefault();
    startProgressiveLecture();
  }

  function openExplore() {
    setCurrentView("explore");
  }

  function openHome() {
    setCurrentView("home");
    setLearningStage("input");
  }

  function toggleInterest(subjectName) {
    setSelectedInterests((previous) => {
      if (previous.includes(subjectName)) {
        return previous.filter((item) => item !== subjectName);
      }

      return [...previous, subjectName];
    });
  }

  function saveExploreInterests() {
    if (selectedInterests.length === 0) {
      return;
    }

    localStorage.setItem(
      "novateach_explore_interests",
      JSON.stringify(selectedInterests),
    );
    setExplorePersonalized(true);
  }

  if (generating) {
    return (
      <main className="generation-screen">
        <section className="generation-container">
          <p className="generation-brand">NOVATEACH</p>

          <div className="generation-content">
            <p className="generation-label">PREPARING YOUR LEARNING EXPERIENCE</p>
            <h1 className="generation-title">Building your lesson.</h1>
            <p className="generation-topic">{topic}</p>

            <div className="generation-progress">
              <div className="generation-progress-line" />
            </div>

            <p className="generation-insight">{learningInsights[0]}</p>
          </div>
        </section>
      </main>
    );
  }

  if (personalizationIntro && authenticatedUser) {
    return (
      <main className="personalization-intro-screen">
        <p className="personalization-intro-brand">NOVATEACH</p>

        <div className="personalization-intro-content">
          <p className="personalization-intro-label">PERSONALIZED LEARNING</p>

          <h1 className="personalization-intro-title">
            Before we teach you,
            <br />
            we want to know you.
          </h1>

          <p className="personalization-intro-subtitle">
            A few thoughtful questions will help Novateach shape how it explains,
            supports, and paces your learning.
          </p>

          <button
            type="button"
            className="personalization-intro-button"
            onClick={startPersonalization}
          >
            Personalize my learning
          </button>
        </div>
      </main>
    );
  }

  if (personalizing && authenticatedUser) {
    const question = personalizationQuestions[questionIndex];
    const progress = ((questionIndex + 1) / personalizationQuestions.length) * 100;
    const isLast = questionIndex === personalizationQuestions.length - 1;

    return (
      <main className="learning-screen">
        <section className="learning-container">
          <p className="learning-brand">NOVATEACH</p>

          <div className="personalization-panel">
            <div className="personalization-progress">
              <span>
                {String(questionIndex + 1).padStart(2, "0")} / {String(personalizationQuestions.length).padStart(2, "0")}
              </span>

              <div className="progress-track">
                <div
                  className="progress-fill"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            <p className="tutor-label">PERSONALIZATION</p>

            <h1 className="personalization-question">{question.label}</h1>

            <div className="personalization-options">
              {question.options.map((option) => (
                <button
                  key={option}
                  type="button"
                  className={`personalization-option ${
                    answers[question.key] === option ? "is-selected" : ""
                  }`}
                  onClick={() => handleOptionSelect(option)}
                  disabled={savingPersonalization}
                >
                  <span className="option-marker" />
                  <span>{option}</span>
                </button>
              ))}
            </div>

            {questionIndex > 0 && (
              <button
                type="button"
                className="question-back-button"
                onClick={handleBackQuestion}
                disabled={savingPersonalization}
              >
                ← Back
              </button>
            )}

            {isLast && (
              <div className="personalization-extra">
                <p className="extra-label">OPTIONAL — SOMETHING ELSE?</p>

                <textarea
                  value={extraInfo}
                  onChange={(event) => setExtraInfo(event.target.value)}
                  placeholder="Anything else you want Novateach to know?"
                  rows={4}
                  disabled={savingPersonalization}
                />

                {personalizationMessage && (
                  <p className="auth-message">{personalizationMessage}</p>
                )}

                <button
                  type="button"
                  className="finish-personalization"
                  onClick={handleFinishPersonalization}
                  disabled={savingPersonalization}
                >
                  {savingPersonalization ? "Creating your environment..." : "Continue"}
                </button>
              </div>
            )}
          </div>
        </section>
      </main>
    );
  }

  if (currentView === "lecture" && lectureSession) {
    const page = currentLecturePage?.page;
    const isPrerequisiteLecture = lectureSession.session_type === "prerequisite";
    const mainPageCount = lectureSession.main_pages?.length || 0;
    const isFinalPage =
      Boolean(currentLecturePage?.is_final_page) || lecturePageNumber >= mainPageCount;

    if (quizMode) {
      return (
        <main
          className={`lecture-shell ${
            isPrerequisiteLecture ? "prerequisite-lecture-shell" : ""
          }`}
        >
          <section className="lecture-reader">
            {isPrerequisiteLecture && (
              <div className="prerequisite-banner">
                <p className="prerequisite-banner-label">FOUNDATION LESSON</p>
                <h2>Prerequisite page</h2>
                <p>
                  Strengthen this foundation before continuing with your main lecture.
                </p>
                <p className="prerequisite-banner-note">
                  You can return to your lecture after completing these pages, or skip this prerequisite anytime.
                </p>
              </div>
            )}

            <p className="page-label">LECTURE COMPLETE</p>
            <h1>Ready to check your understanding?</h1>
            <p>
              You have completed the guided lecture. The quiz will measure what you understood and help choose your next step.
            </p>

            <button
              type="button"
              className="lecture-action-button"
              onClick={() => setQuizMode(false)}
            >
              Back to lesson
            </button>
          </section>
        </main>
      );
    }

    return (
      <main
        className={`lecture-shell ${
          isPrerequisiteLecture ? "prerequisite-lecture-shell" : ""
        }`}
      >
        {selectedPrerequisite && (
          <div className="prerequisite-overlay">
            <div className="prerequisite-panel">
              <button
                type="button"
                className="prerequisite-close"
                onClick={() => setSelectedPrerequisite(null)}
              >
                ×
              </button>

              <p className="page-label">RECOMMENDED FOUNDATION</p>
              <h2>{selectedPrerequisite.title}</h2>
              <p>{selectedPrerequisite.reason || selectedPrerequisite.objective}</p>
              <p>Estimated time: {selectedPrerequisite.estimated_minutes} minutes</p>

              <div className="prerequisite-actions">
                <button
                  type="button"
                  className="lecture-action-button"
                  onClick={continueWithOriginalLecture}
                >
                  Continue with lecture
                </button>

                <button
                  type="button"
                  className="lecture-secondary-button"
                  onClick={skipPrerequisite}
                >
                  Return without continuing
                </button>

                <button
                  type="button"
                  onClick={() => startPrerequisite(selectedPrerequisite.node_id)}
                  disabled={prerequisiteLoading}
                >
                  {prerequisiteLoading ? "Preparing..." : "Learn this prerequisite"}
                </button>

                <button
                  type="button"
                  onClick={() => setSelectedPrerequisite(null)}
                >
                  Back to lecture
                </button>
              </div>
            </div>
          </div>
        )}

        {isPrerequisiteLecture && !isFinalPage && (
          <div className="prerequisite-skip">
            <button
              type="button"
              className="lecture-secondary-button"
              onClick={skipPrerequisite}
              disabled={pageLoading}
            >
              Skip prerequisite and return
            </button>
          </div>
        )}

        <LectureContents
          prerequisites={lectureSession.prerequisites}
          mainPages={lectureSession.main_pages}
          currentPage={lecturePageNumber}
          onPrerequisiteClick={handlePrerequisiteClick}
          onPageClick={(pageNumber) =>
            loadLecturePage(lectureSession.session_id, pageNumber)
          }
        />

        <section className="lecture-reader">
          <button
            type="button"
            className="lecture-back-button"
            onClick={openHome}
          >
            ← Learning space
          </button>

          {lectureError && <p className="lecture-error">{lectureError}</p>}
          {pageLoading && <p className="lecture-status">Loading the next page…</p>}

          {page && (
            <>
              <p className="page-label">
                PAGE {lecturePageNumber} OF {lectureSession.main_pages.length}
              </p>

              <h1>{page.title}</h1>

              <p className="page-objective">{page.objective}</p>

              {page.introduction && <p>{page.introduction}</p>}
              {page.section?.purpose && <p>{page.section.purpose}</p>}
              {page.section?.explanation && <p>{page.section.explanation}</p>}

              {page.section?.intuition && (
                <div className="lecture-note">
                  <span>INTUITION</span>
                  <p>{page.section.intuition}</p>
                </div>
              )}

              {page.section?.analogy && (
                <div className="lecture-note">
                  <span>ANALOGY</span>
                  <p>{page.section.analogy}</p>
                </div>
              )}

              {page.section?.worked_examples?.map((example, index) => (
                <div className="lecture-example" key={`${page.node_id}-example-${index}`}>
                  <p className="lecture-label">WORKED EXAMPLE</p>
                  <h2>{example.question}</h2>

                  {example.thinking_steps?.length > 0 && (
                    <ol>
                      {example.thinking_steps.map((step, stepIndex) => (
                        <li key={`${page.node_id}-step-${stepIndex}`}>{step}</li>
                      ))}
                    </ol>
                  )}

                  {example.solution && <p>{example.solution}</p>}
                  {example.takeaway && <p>{example.takeaway}</p>}
                </div>
              ))}

              {page.section?.common_mistakes?.length > 0 && (
                <div className="lecture-note">
                  <span>WATCH OUT FOR</span>
                  <ul>
                    {page.section.common_mistakes.map((mistake, index) => (
                      <li key={`${page.node_id}-mistake-${index}`}>{mistake}</li>
                    ))}
                  </ul>
                </div>
              )}

              {lectureSession.session_type === "prerequisite" && isFinalPage ? (
                <div className="prerequisite-complete">
                  <p className="page-label">FOUNDATION COMPLETE</p>
                  <h2>You can now continue with your original topic.</h2>

                  <div className="lecture-actions">
                    <button
                      type="button"
                      className="lecture-action-button"
                      onClick={continueWithOriginalLecture}
                    >
                      Continue with lecture
                    </button>

                    <button
                      type="button"
                      className="lecture-secondary-button"
                      onClick={() => loadLecturePage(lectureSession.session_id, 1)}
                    >
                      Review prerequisite
                    </button>
                  </div>
                </div>
              ) : (
                <div className="lecture-actions">
                  {isFinalPage ? (
                    <button
                      type="button"
                      className="lecture-action-button"
                      onClick={() => setQuizMode(true)}
                    >
                      Start quiz
                    </button>
                  ) : (
                    <button
                      type="button"
                      className="lecture-action-button"
                      onClick={continueLecture}
                      disabled={pageLoading}
                    >
                      Continue
                    </button>
                  )}
                </div>
              )}
            </>
          )}
        </section>
      </main>
    );
  }

  if (currentView === "explore" && authenticatedUser) {
    return (
      <main className="explore-screen">
        <section className="explore-container">
          <header className="learning-home-header">
            <button
              type="button"
              className="learning-home-brand"
              onClick={openHome}
            >
              NOVATEACH
            </button>

            <button
              type="button"
              className="explore-header-button"
              onClick={openHome}
            >
              Home
            </button>
          </header>

          {!explorePersonalized ? (
            <div className="explore-intro">
              <p className="explore-label">MAKE EXPLORE YOURS</p>

              <h1 className="explore-title">What are you curious about?</h1>

              <p className="explore-subtitle">
                Choose a few areas that genuinely interest you.
              </p>

              <div className="interest-grid">
                {interestOptions.map((interest) => (
                  <button
                    key={interest}
                    type="button"
                    className={`interest-option ${
                      selectedInterests.includes(interest) ? "is-selected" : ""
                    }`}
                    onClick={() => toggleInterest(interest)}
                  >
                    <span className="interest-marker" />
                    <span>{interest}</span>
                  </button>
                ))}
              </div>

              <button
                type="button"
                className="explore-save-button"
                disabled={selectedInterests.length === 0}
                onClick={saveExploreInterests}
              >
                Build my Explore →
              </button>
            </div>
          ) : (
            <div className="explore-content">
              <p className="explore-label">CURATED FOR YOU</p>

              <h1 className="explore-title">Explore something interesting.</h1>

              {personalizedSubjects.map((subject) => (
                <section key={subject.id} className="explore-subject-section">
                  <h2>{subject.name}</h2>
                  <p>{subject.description}</p>

                  <div className="explore-topic-grid">
                    {subject.topics.map((subjectTopic) => (
                      <button
                        key={subjectTopic.name}
                        type="button"
                        className="explore-topic-card"
                        onClick={() => {
                          setTopic(subjectTopic.name);
                          openHome();
                        }}
                      >
                        <span>{subjectTopic.name}</span>
                        <small>{subjectTopic.description}</small>
                      </button>
                    ))}
                  </div>
                </section>
              ))}
            </div>
          )}
        </section>
      </main>
    );
  }

  if (
    currentView === "home" &&
    authenticatedUser &&
    learningStage === "subject" &&
    topicResolution
  ) {
    return (
      <main className="learning-home-screen">
        <section className="learning-home-container">
          <header className="learning-home-header">
            <button
              type="button"
              className="learning-home-brand"
              onClick={openHome}
            >
              NOVATEACH
            </button>
          </header>

          <div className="subject-selection-content">
            <p className="learning-home-label">LET&apos;S MAKE THIS SPECIFIC</p>

            <h1>Which subject do you mean?</h1>

            <p>&quot;{topic}&quot;</p>

            <p>
              {topicResolution.reason || "This topic can belong to more than one subject."}
            </p>

            <div className="subject-options">
              {topicResolution.possible_subjects?.map((subject) => (
                <button
                  key={subject}
                  type="button"
                  className="subject-option"
                  onClick={() => handleSubjectSelect(subject)}
                  disabled={generating}
                >
                  <span>{subject}</span>
                  <span>→</span>
                </button>
              ))}
            </div>

            {learningError && <p className="learning-error">{learningError}</p>}

            <button
              type="button"
              className="learning-back-link"
              onClick={resetLearningFlow}
            >
              ← Change topic
            </button>
          </div>
        </section>
      </main>
    );
  }

  if (currentView === "home" && authenticatedUser) {
    return (
      <main className="learning-home-screen">
        <section className="learning-home-container">
          <header className="learning-home-header">
            <p className="learning-home-brand">NOVATEACH</p>

            <button
              type="button"
              className="learning-home-explore"
              onClick={openExplore}
            >
              Explore ↗
            </button>
          </header>

          <div className="learning-home-content">
            <p className="learning-home-label">YOUR LEARNING SPACE</p>

            <h1 className="learning-home-title">
              What do you want to learn,
              <br />
              <span>{authenticatedUser.name}?</span>
            </h1>

            <form className="topic-input-form" onSubmit={handleTopicSubmit}>
              <input
                type="text"
                value={topic}
                onChange={(event) => setTopic(event.target.value)}
                placeholder="Enter a topic you want to understand..."
              />

              <button
                type="submit"
                className="topic-submit-button"
                disabled={generating}
              >
                {generating ? "..." : "→"}
              </button>
            </form>

            <div className="learning-options">
              <div className="learning-field">
                <label htmlFor="academic-level">ACADEMIC LEVEL</label>

                <input
                  id="academic-level"
                  type="text"
                  value={academicLevel}
                  onChange={(event) => setAcademicLevel(event.target.value)}
                  placeholder="Grade 10 or undergraduate"
                />
              </div>

              <div className="learning-field">
                <label htmlFor="difficulty-level">DIFFICULTY</label>

                <select
                  id="difficulty-level"
                  value={difficultyLevel}
                  onChange={(event) => setDifficultyLevel(event.target.value)}
                >
                  <option value="basic">Basic</option>
                  <option value="standard">Standard</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>
            </div>

            {learningError && <p className="learning-error">{learningError}</p>}

            <div className="learning-home-empty-state">
              <p>
                As you learn, Novateach will begin understanding what you need next.
              </p>
            </div>
          </div>
        </section>
      </main>
    );
  }

  if (currentView === "auth" && showAuth && !authenticatedUser) {
    const isSignup = authMode === "signup";

    return (
      <main className="auth-screen">
        <section className="auth-page-container">
          <p className="auth-page-brand">NOVATEACH</p>

          <div className="auth-page-content">
            <p className="auth-page-label">
              {isSignup ? "CREATE YOUR ACCOUNT" : "WELCOME BACK"}
            </p>

            <h1 className="auth-page-title">
              {isSignup ? (
                <>
                  Let&apos;s make
                  <br />
                  this yours.
                </>
              ) : (
                <>
                  Continue your
                  <br />
                  learning journey.
                </>
              )}
            </h1>

            <p className="auth-page-subtitle">
              {isSignup
                ? "Create your Novateach account before we personalize how you learn."
                : "Sign in to continue with Novateach."}
            </p>

            <form
              className="auth-page-form"
              onSubmit={isSignup ? handleSignup : handleLogin}
            >
              <div className="auth-page-field">
                <label htmlFor="username">USERNAME</label>

                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  placeholder={isSignup ? "Choose a username" : "Your username"}
                  autoComplete="username"
                  disabled={authLoading}
                />
              </div>

              {isSignup && (
                <div className="auth-page-field">
                  <label htmlFor="name">NAME</label>

                  <input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                    placeholder="Your name"
                    autoComplete="name"
                    disabled={authLoading}
                  />
                </div>
              )}

              <div className="auth-page-field">
                <label htmlFor="password">PASSWORD</label>

                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder={isSignup ? "At least 8 characters" : "Your password"}
                  autoComplete={isSignup ? "new-password" : "current-password"}
                  disabled={authLoading}
                />
              </div>

              {authMessage && <p className="auth-page-message">{authMessage}</p>}

              <button
                type="submit"
                className="auth-page-submit"
                disabled={authLoading}
              >
                {authLoading
                  ? "Please wait..."
                  : isSignup
                    ? "Create account"
                    : "Continue"}
              </button>
            </form>

            <button
              type="button"
              className="auth-page-switch"
              onClick={isSignup ? openLogin : openSignup}
              disabled={authLoading}
            >
              {isSignup
                ? "Already have an account? Sign in"
                : "New to Novateach? Create an account"}
            </button>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className={`novateach-app ${started ? "is-started" : ""}`}>
      <section className="entry-screen">
        <div className="entry-stack">
          <p className="brand-mark">NOVATEACH</p>

          <div className="entry-content">
            <h1 className="entry-title">
              Learning that <span>ADAPTS</span>
            </h1>

            <p className="entry-subtitle">
              Novateach understands how you learn and helps you discover what to learn next.
            </p>

            <button
              type="button"
              className="enter-button"
              onClick={handleEnter}
              disabled={isEntering}
            >
              {isEntering ? "Entering..." : "Enter Novateach"}
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}

export default App;
