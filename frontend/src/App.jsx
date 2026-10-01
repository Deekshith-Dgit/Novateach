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
  "Science",
  "Physics",
  "Biology",
  "Chemistry",
  "Astronomy",
  "Earth Science",
  "Environmental Science",
  "Computer Science",
  "Engineering",
  "Psychology",
  "Sociology",
  "Philosophy",
  "Economics",
  "History",
  "Literature",
  "Linguistics",
  "Political Science",
  "Anthropology",
  "Health Science",
  "Art and Design",
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
      {
        name: "Linear Algebra",
        description: "Study vectors, matrices, and transformations.",
      },
      {
        name: "Number Theory",
        description: "Explore integers, primes, and number patterns.",
      },
      {
        name: "Geometry",
        description: "Understand shapes, space, and geometric reasoning.",
      },
      {
        name: "Trigonometry",
        description: "Connect angles, triangles, and periodic patterns.",
      },
      {
        name: "Discrete Mathematics",
        description: "Explore logic, sets, graphs, and counting.",
      },
      {
        name: "Mathematical Logic",
        description: "Build precise arguments from statements and rules.",
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
      {
        name: "Thermodynamics",
        description: "Explore heat, energy, and physical change.",
      },
      {
        name: "Optics",
        description: "Study light, lenses, and image formation.",
      },
      {
        name: "Quantum Physics",
        description: "Meet the principles that describe matter at small scales.",
      },
      {
        name: "Relativity",
        description: "Explore space, time, motion, and gravity.",
      },
      {
        name: "Electricity and Circuits",
        description: "Understand current, voltage, and electrical systems.",
      },
      {
        name: "Energy and Conservation",
        description: "Track how energy moves and changes form.",
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
      {
        name: "Data Structures",
        description: "Organize information for efficient computation.",
      },
      {
        name: "Databases",
        description: "Model, store, and retrieve structured information.",
      },
      {
        name: "Computer Networks",
        description: "Understand how devices communicate across networks.",
      },
      {
        name: "Cybersecurity",
        description: "Learn how digital systems are protected.",
      },
      {
        name: "Operating Systems",
        description: "Explore how computers manage programs and resources.",
      },
      {
        name: "Theory of Computation",
        description: "Study what problems computers can solve.",
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
      {
        name: "Learning and Cognition",
        description: "Understand attention, reasoning, and learning.",
      },
      {
        name: "Developmental Psychology",
        description: "Explore how people change throughout life.",
      },
      {
        name: "Social Psychology",
        description: "Study how social settings shape behaviour.",
      },
      {
        name: "Emotion and Motivation",
        description: "Understand the processes that guide feelings and action.",
      },
      {
        name: "Perception",
        description: "Explore how the mind interprets sensory information.",
      },
      {
        name: "Personality",
        description: "Examine patterns in how individuals think and behave.",
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
      {
        name: "Evolution",
        description: "Explore how populations change across generations.",
      },
      {
        name: "Human Biology",
        description: "Understand the systems that keep the body functioning.",
      },
      {
        name: "Microbiology",
        description: "Study microorganisms and their roles in life.",
      },
      {
        name: "Neuroscience",
        description: "Explore the nervous system and how the brain works.",
      },
      {
        name: "Plant Biology",
        description: "Understand plant structure, growth, and adaptation.",
      },
      {
        name: "Biotechnology",
        description: "Explore how living systems can solve practical problems.",
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
      {
        name: "Supply and Demand",
        description: "Understand how markets coordinate buyers and sellers.",
      },
      {
        name: "Market Structures",
        description: "Compare competition across different kinds of markets.",
      },
      {
        name: "Inflation",
        description: "Explore changes in prices and purchasing power.",
      },
      {
        name: "Economic Growth",
        description: "Understand how economies expand and develop.",
      },
      {
        name: "Behavioural Economics",
        description: "Study how real human choices shape economic outcomes.",
      },
      {
        name: "International Trade",
        description: "Explore exchange, specialization, and global markets.",
      },
    ],
  },
  {
    id: "science",
    name: "Science",
    description: "Investigate evidence, explanations, and the natural world.",
    topics: [
      {
        name: "Scientific Method",
        description: "Form questions, test ideas, and interpret evidence.",
      },
      {
        name: "How to Read a Scientific Study",
        description: "Evaluate methods, results, and research claims.",
      },
      {
        name: "Scientific Models",
        description: "Understand how models explain and predict phenomena.",
      },
      {
        name: "Evidence and Uncertainty",
        description: "Reason carefully about data, measurement, and confidence.",
      },
      {
        name: "Classification of Matter",
        description: "Organize materials by their properties and composition.",
      },
      {
        name: "Energy in Natural Systems",
        description: "Trace how energy flows through physical and living systems.",
      },
    ],
  },
  {
    id: "chemistry",
    name: "Chemistry",
    description: "Explore the composition, properties, and changes of matter.",
    topics: [
      {
        name: "Atomic Structure",
        description: "Understand the particles and organization within atoms.",
      },
      {
        name: "Chemical Bonding",
        description: "Explore why atoms join to form molecules and materials.",
      },
      {
        name: "Chemical Reactions",
        description: "Understand how substances transform into new substances.",
      },
      {
        name: "Acids and Bases",
        description: "Compare important chemical behaviours in solutions.",
      },
      {
        name: "Organic Chemistry",
        description: "Study the structures and reactions of carbon compounds.",
      },
      {
        name: "The Periodic Table",
        description: "Discover patterns in the properties of elements.",
      },
      {
        name: "Solutions and Concentration",
        description: "Understand mixtures and how dissolved substances are described.",
      },
    ],
  },
  {
    id: "astronomy",
    name: "Astronomy",
    description: "Study planets, stars, galaxies, and the wider universe.",
    topics: [
      {
        name: "The Solar System",
        description: "Explore the Sun, planets, moons, and smaller bodies.",
      },
      {
        name: "Stars and Stellar Life Cycles",
        description: "Understand how stars form, evolve, and change.",
      },
      {
        name: "Galaxies",
        description: "Explore the structure and variety of galactic systems.",
      },
      {
        name: "Black Holes",
        description: "Understand what happens in regions of extreme gravity.",
      },
      {
        name: "Cosmology",
        description: "Investigate the history and large-scale structure of the universe.",
      },
      {
        name: "Exoplanets",
        description: "Learn how planets around other stars are discovered.",
      },
    ],
  },
  {
    id: "earth-science",
    name: "Earth Science",
    description: "Understand Earth's materials, processes, and changing systems.",
    topics: [
      {
        name: "Plate Tectonics",
        description: "Explore how moving plates shape Earth's surface.",
      },
      {
        name: "Rocks and the Rock Cycle",
        description: "Understand how rocks form and transform over time.",
      },
      {
        name: "Weather and Climate",
        description: "Distinguish atmospheric conditions from long-term patterns.",
      },
      {
        name: "Oceans and Currents",
        description: "Explore ocean circulation and its effects on Earth.",
      },
      {
        name: "The Water Cycle",
        description: "Trace water through the atmosphere, land, and oceans.",
      },
      {
        name: "Natural Hazards",
        description: "Understand earthquakes, volcanoes, and risk reduction.",
      },
    ],
  },
  {
    id: "environmental-science",
    name: "Environmental Science",
    description: "Study interactions between people, organisms, and environments.",
    topics: [
      {
        name: "Biodiversity",
        description: "Understand variety in life and why it matters.",
      },
      {
        name: "Climate Change",
        description: "Explore causes, evidence, impacts, and responses.",
      },
      {
        name: "Ecosystem Services",
        description: "Learn how healthy ecosystems support human life.",
      },
      {
        name: "Renewable Energy",
        description: "Compare energy sources and their environmental trade-offs.",
      },
      {
        name: "Pollution and Public Health",
        description: "Understand how contaminants affect communities and ecosystems.",
      },
      {
        name: "Conservation",
        description: "Explore approaches to protecting species and habitats.",
      },
    ],
  },
  {
    id: "engineering",
    name: "Engineering",
    description: "Use design, evidence, and systems thinking to solve problems.",
    topics: [
      {
        name: "Engineering Design",
        description: "Move from a real need to a tested design solution.",
      },
      {
        name: "Robotics",
        description: "Understand sensors, control, and automated machines.",
      },
      {
        name: "Structural Engineering",
        description: "Explore how structures carry loads and remain stable.",
      },
      {
        name: "Electrical Engineering",
        description: "Study circuits, signals, and electrical systems.",
      },
      {
        name: "Materials Science",
        description: "Connect material structure to useful properties.",
      },
      {
        name: "Systems Engineering",
        description: "Design complex systems to work together reliably.",
      },
    ],
  },
  {
    id: "philosophy",
    name: "Philosophy",
    description: "Examine fundamental questions through careful reasoning.",
    topics: [
      {
        name: "Logic and Arguments",
        description: "Identify premises, conclusions, and sound reasoning.",
      },
      {
        name: "Ethics",
        description: "Explore how we reason about right action and good lives.",
      },
      {
        name: "Epistemology",
        description: "Ask what knowledge is and how beliefs are justified.",
      },
      {
        name: "Political Philosophy",
        description: "Examine justice, rights, authority, and the common good.",
      },
      {
        name: "Philosophy of Science",
        description: "Explore evidence, explanation, and scientific knowledge.",
      },
      {
        name: "Philosophy of Mind",
        description: "Investigate consciousness, thought, and personal identity.",
      },
      {
        name: "Ancient Philosophy",
        description: "Meet foundational questions from early philosophical traditions.",
      },
    ],
  },
  {
    id: "sociology",
    name: "Sociology",
    description: "Understand how social groups and institutions shape human life.",
    topics: [
      {
        name: "Culture and Society",
        description: "Explore shared meanings, norms, and social practices.",
      },
      {
        name: "Socialization",
        description: "Understand how people learn roles and expectations.",
      },
      {
        name: "Social Inequality",
        description: "Examine how resources and opportunities are distributed.",
      },
      {
        name: "Families and Relationships",
        description: "Study how family structures and relationships change.",
      },
      {
        name: "Education and Society",
        description: "Explore how education reflects and shapes social life.",
      },
      {
        name: "Organizations and Institutions",
        description: "Understand how institutions organize collective activity.",
      },
      {
        name: "Social Change",
        description: "Investigate how societies transform over time.",
      },
    ],
  },
  {
    id: "history",
    name: "History",
    description: "Interpret the past through sources, context, and evidence.",
    topics: [
      {
        name: "Ancient Civilizations",
        description: "Compare early societies and the systems they built.",
      },
      {
        name: "World History",
        description: "Connect events and societies across regions and eras.",
      },
      {
        name: "Industrial Revolution",
        description: "Explore how industry transformed work and society.",
      },
      {
        name: "History of Science",
        description: "Trace how scientific ideas and methods developed.",
      },
      {
        name: "Historical Thinking",
        description: "Use sources and context to evaluate claims about the past.",
      },
      {
        name: "Modern History",
        description: "Examine major changes shaping the contemporary world.",
      },
    ],
  },
  {
    id: "literature",
    name: "Literature",
    description: "Read stories, poems, and drama with attention to meaning and form.",
    topics: [
      {
        name: "Reading a Novel",
        description: "Explore character, structure, setting, and interpretation.",
      },
      {
        name: "Poetry",
        description: "Understand imagery, sound, rhythm, and poetic form.",
      },
      {
        name: "Shakespeare",
        description: "Read dramatic language, character, and historical context.",
      },
      {
        name: "Literary Devices",
        description: "Recognize how writers create emphasis and meaning.",
      },
      {
        name: "World Literature",
        description: "Encounter literary traditions across languages and cultures.",
      },
      {
        name: "Creative Writing",
        description: "Develop voice, scenes, and compelling narrative structure.",
      },
    ],
  },
  {
    id: "linguistics",
    name: "Linguistics",
    description: "Explore how language is structured, learned, and used.",
    topics: [
      {
        name: "Phonetics",
        description: "Study how speech sounds are produced and perceived.",
      },
      {
        name: "Grammar and Syntax",
        description: "Understand how words combine into meaningful sentences.",
      },
      {
        name: "Meaning and Semantics",
        description: "Explore how language expresses meaning.",
      },
      {
        name: "Language Change",
        description: "Investigate how languages evolve through time.",
      },
      {
        name: "Sociolinguistics",
        description: "Study the relationship between language and society.",
      },
      {
        name: "How Children Learn Language",
        description: "Explore patterns in language acquisition and development.",
      },
    ],
  },
  {
    id: "political-science",
    name: "Political Science",
    description: "Study power, government, institutions, and public life.",
    topics: [
      {
        name: "Democracy",
        description: "Understand participation, representation, and accountability.",
      },
      {
        name: "Constitutions and Law",
        description: "Explore how legal frameworks shape government.",
      },
      {
        name: "Political Ideologies",
        description: "Compare ideas about freedom, equality, and authority.",
      },
      {
        name: "International Relations",
        description: "Study cooperation and conflict among states.",
      },
      {
        name: "Public Policy",
        description: "Understand how governments respond to public issues.",
      },
      {
        name: "Elections and Representation",
        description: "Explore how votes become political representation.",
      },
    ],
  },
  {
    id: "anthropology",
    name: "Anthropology",
    description: "Understand human cultures, histories, and ways of life.",
    topics: [
      {
        name: "Cultural Anthropology",
        description: "Explore how people create meaning in everyday life.",
      },
      {
        name: "Archaeology",
        description: "Interpret past societies through material evidence.",
      },
      {
        name: "Human Evolution",
        description: "Trace the biological and cultural history of humanity.",
      },
      {
        name: "Language and Culture",
        description: "Examine how language both reflects and shapes culture.",
      },
      {
        name: "Kinship and Communities",
        description: "Understand relationships, families, and social organization.",
      },
      {
        name: "Anthropological Fieldwork",
        description: "Learn how researchers study communities ethically.",
      },
    ],
  },
  {
    id: "health-science",
    name: "Health Science",
    description: "Learn how bodies, health systems, and wellbeing are understood.",
    topics: [
      {
        name: "Human Anatomy",
        description: "Explore the structure of the human body.",
      },
      {
        name: "Physiology",
        description: "Understand how body systems function and interact.",
      },
      {
        name: "Nutrition",
        description: "Explore nutrients, food, and the body's needs.",
      },
      {
        name: "Public Health",
        description: "Study how communities prevent illness and support health.",
      },
      {
        name: "Immunology",
        description: "Understand how the immune system responds to threats.",
      },
      {
        name: "Epidemiology",
        description: "Learn how patterns of health and disease are studied.",
      },
    ],
  },
  {
    id: "art-and-design",
    name: "Art and Design",
    description: "Explore visual ideas, creative practice, and design principles.",
    topics: [
      {
        name: "Design Principles",
        description: "Use hierarchy, balance, contrast, and alignment.",
      },
      {
        name: "Color Theory",
        description: "Understand relationships between colors and visual effects.",
      },
      {
        name: "Art History",
        description: "Connect artworks with the movements and contexts around them.",
      },
      {
        name: "Drawing Fundamentals",
        description: "Practice observation, proportion, form, and value.",
      },
      {
        name: "Typography",
        description: "Explore how type communicates through form and layout.",
      },
      {
        name: "Visual Communication",
        description: "Use images and composition to communicate ideas clearly.",
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
  const [lectureFeedback, setLectureFeedback] = useState("");
  const [showLectureFeedback, setShowLectureFeedback] = useState(false);
  const [completionLoading, setCompletionLoading] = useState(false);
  const [completionError, setCompletionError] = useState("");

  const [selectedPrerequisite, setSelectedPrerequisite] = useState(null);
  const [prerequisiteLoading, setPrerequisiteLoading] = useState(false);
  const [quiz, setQuiz] = useState(null);
  const [quizAnswers, setQuizAnswers] = useState({});
  const [quizQuestionIndex, setQuizQuestionIndex] = useState(0);
  const [quizResult, setQuizResult] = useState(null);
  const [quizLoading, setQuizLoading] = useState(false);
  const [quizError, setQuizError] = useState("");

  const [doubtText, setDoubtText] = useState("");
  const [doubtResponse, setDoubtResponse] = useState(null);
  const [doubtLoading, setDoubtLoading] = useState(false);
  const [doubtError, setDoubtError] = useState("");

  const [dashboard, setDashboard] = useState(null);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [dashboardError, setDashboardError] = useState("");
  const [exploreMessage, setExploreMessage] = useState("");
  const [savedExploreInterests, setSavedExploreInterests] = useState([]);
  const [selectedExploreTopic, setSelectedExploreTopic] = useState(null);
  const [savingExploreInterest, setSavingExploreInterest] = useState(false);
  const [exploreSearch, setExploreSearch] = useState("");
  const [activeExploreSubject, setActiveExploreSubject] = useState("All areas");
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

  const visibleExploreSubjects = useMemo(() => {
    const search = exploreSearch.trim().toLowerCase();

    return personalizedSubjects
      .filter(
        (subject) =>
          activeExploreSubject === "All areas" ||
          subject.name === activeExploreSubject,
      )
      .map((subject) => ({
        ...subject,
        topics: subject.topics.filter(
          (subjectTopic) =>
            !search ||
            subjectTopic.name.toLowerCase().includes(search) ||
            subjectTopic.description.toLowerCase().includes(search) ||
            subject.name.toLowerCase().includes(search) ||
            subject.description.toLowerCase().includes(search),
        ),
      }))
      .filter((subject) => subject.topics.length > 0);
  }, [activeExploreSubject, exploreSearch, personalizedSubjects]);

  const exploreTopicCount = useMemo(
    () =>
      visibleExploreSubjects.reduce(
        (total, subject) => total + subject.topics.length,
        0,
      ),
    [visibleExploreSubjects],
  );

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
    setLectureFeedback("");
    setShowLectureFeedback(false);
    setCompletionError("");
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
    setLectureFeedback("");
    setShowLectureFeedback(false);
    setCompletionError("");
    setDoubtText("");
    setDoubtResponse(null);
    setDoubtError("");
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

  useEffect(() => {
    if (!selectedExploreTopic) {
      return undefined;
    }

    function handleEscape(event) {
      if (event.key === "Escape") {
        setSelectedExploreTopic(null);
      }
    }

    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [selectedExploreTopic]);

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


  async function startQuiz() {
  setQuizQuestionIndex(0);
  setQuizLoading(true);
  setQuizError("");
  setQuizResult(null);
  setQuizAnswers({});
  setQuiz(null);
  setQuizMode(true);

  try {
    const response = await fetch(
      `${API_BASE}/api/quiz/generate`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: authenticatedUser.username,
          topic,
          session_id:
            lectureSession?.session_id || null,
          academic_level: academicLevel,
          difficulty: difficultyLevel,
          question_count: 5,
        }),
      },
    );

    const data = await readResponse(response);

    if (!response.ok) {
      throw new Error(
        data.detail ||
          "Could not generate quiz.",
      );
    }

    setQuiz(data);
  } catch (error) {
    setQuizError(error.message);
  } finally {
    setQuizLoading(false);
  }
}

async function finishLecture() {
  if (!lectureSession || lectureSession.session_type === "prerequisite") {
    return;
  }

  setCompletionLoading(true);
  setCompletionError("");

  try {
    const response = await fetch(
      `${API_BASE}/api/lecture/${lectureSession.session_id}/complete`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: authenticatedUser.username,
        }),
      },
    );
    const data = await readResponse(response);

    if (!response.ok) {
      throw new Error(data.detail || "Could not complete this lecture.");
    }

    setShowLectureFeedback(true);
  } catch (error) {
    console.error(error);
    setCompletionError(error.message || "Could not complete this lecture.");
  } finally {
    setCompletionLoading(false);
  }
}

function goToNextQuizQuestion() {
  if (!quiz) {
    return;
  }

  if (!quizAnswers[quiz.questions[quizQuestionIndex]?.id]) {
    return;
  }

  if (quizQuestionIndex >= quiz.questions.length - 1) {
    submitQuiz();
    return;
  }

  setQuizQuestionIndex((previous) => previous + 1);
}

function continueToQuiz() {
  setShowLectureFeedback(false);
  if (quiz) {
    setQuizMode(true);
    return;
  }
  startQuiz();
}


function chooseQuizAnswer(
  questionId,
  answer,
) {
  setQuizAnswers((previous) => ({
    ...previous,
    [questionId]: answer,
  }));
}


async function submitQuiz() {
  setQuizLoading(true);
  setQuizError("");

  try {
    const response = await fetch(
      `${API_BASE}/api/quiz/submit`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: authenticatedUser.username,
          quiz_id: quiz.quiz_id,
          answers: quizAnswers,
          lecture_feedback: lectureFeedback,
        }),
      },
    );

    const data = await readResponse(response);

    if (!response.ok) {
      throw new Error(
        data.detail ||
          "Could not submit quiz.",
      );
    }

    setQuizResult(data);
  } catch (error) {
    setQuizError(error.message);
  } finally {
    setQuizLoading(false);
  }
}


async function submitDoubt(event) {
  event.preventDefault();

  if (!doubtText.trim()) {
    setDoubtError("Write your doubt first.");
    return;
  }

  setDoubtLoading(true);
  setDoubtError("");

  try {
    const response = await fetch(
      `${API_BASE}/api/doubt/resolve`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: authenticatedUser.username,
          question: doubtText,
          topic,
          session_id:
            lectureSession?.session_id || null,
          page_number: lecturePageNumber,
        }),
      },
    );

    const data = await readResponse(response);

    if (!response.ok) {
      throw new Error(
        data.detail ||
          "Could not resolve doubt.",
      );
    }

    setDoubtResponse(data.response);
  } catch (error) {
    setDoubtError(error.message);
  } finally {
    setDoubtLoading(false);
  }
}


async function loadDashboard() {
  setDashboardLoading(true);
  setDashboardError("");

  try {
    const response = await fetch(
      `${API_BASE}/api/dashboard/`
        + authenticatedUser.username,
    );

    const data = await readResponse(response);

    if (!response.ok) {
      throw new Error(
        data.detail ||
          "Could not load dashboard.",
      );
    }

    setDashboard(data);
    setSavedExploreInterests(data.profile?.saved_interests || []);
  } catch (error) {
    console.error(error);
    setDashboardError(error.message || "Could not load dashboard.");
  } finally {
    setDashboardLoading(false);
  }
}
  function handleTopicSubmit(event) {
    event.preventDefault();
    startProgressiveLecture();
  }

  function openExplore() {
    setCurrentView("explore");
    setSelectedExploreTopic(null);
    loadDashboard();
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

    try {
      localStorage.setItem(
        "novateach_explore_interests",
        JSON.stringify(selectedInterests),
      );
      setExplorePersonalized(true);
      setExploreMessage("");
    } catch (error) {
      console.error(error);
      setExploreMessage("Could not save your interests on this device.");
    }
  }

  async function persistExploreInterest(topicName, subjectName, status) {
    const response = await fetch(`${API_BASE}/api/profile/interests`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: authenticatedUser.username,
        topic: topicName,
        subject: subjectName,
        status,
      }),
    });
    const data = await readResponse(response);

    if (!response.ok || data.status !== "success") {
      throw new Error(
        data.detail || "Could not update your saved interests.",
      );
    }

    const interests = data.saved_interests || [];
    setSavedExploreInterests(interests);
    setDashboard((previous) =>
      previous
        ? {
            ...previous,
            profile: {
              ...previous.profile,
              saved_interests: interests,
            },
          }
        : previous,
    );
    return interests;
  }

  async function saveExploreTopic(status) {
    if (!selectedExploreTopic) {
      return;
    }

    setSavingExploreInterest(true);
    setExploreMessage("");
    try {
      await persistExploreInterest(
        selectedExploreTopic.topic.name,
        selectedExploreTopic.subject.name,
        status,
      );
      setSelectedExploreTopic(null);
    } catch (error) {
      console.error(error);
      setExploreMessage(error.message);
    } finally {
      setSavingExploreInterest(false);
    }
  }

  async function removeSavedExploreTopic(topicName, subjectName) {
    setDashboardError("");
    try {
      await persistExploreInterest(topicName, subjectName, "remove");
    } catch (error) {
      console.error(error);
      setDashboardError(error.message);
    }
  }

  function openDashboard() {
    setDashboard(null);
    setCurrentView("dashboard");
    loadDashboard();
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
        <main className="quiz-screen">
          {quizLoading && !quiz ? (
            <section
              className="quiz-building"
              role="status"
              aria-live="polite"
              aria-label={`Generating a quiz about ${topic}`}
            >
              <div className="quiz-building-visual" aria-hidden="true">
                <div className="quiz-building-orbit quiz-building-orbit-outer" />
                <div className="quiz-building-orbit quiz-building-orbit-inner" />
                <div className="quiz-building-card quiz-building-card-back">
                  <span>03</span>
                  <i />
                  <i />
                  <i />
                </div>
                <div className="quiz-building-card quiz-building-card-middle">
                  <span>02</span>
                  <i />
                  <i />
                  <i />
                </div>
                <div className="quiz-building-card quiz-building-card-front">
                  <span>01</span>
                  <b />
                  <i />
                  <i />
                  <i />
                  <div className="quiz-building-card-scan" />
                </div>
                <span className="quiz-building-point quiz-building-point-one" />
                <span className="quiz-building-point quiz-building-point-two" />
                <span className="quiz-building-point quiz-building-point-three" />
              </div>

              <p className="quiz-building-eyebrow">NOVATEACH · ACTIVE RECALL</p>
              <h1>Preparing your quiz</h1>
              <p className="quiz-building-topic">{topic}</p>
              <p className="quiz-building-description">
                Shaping a focused set of questions around what you just learned.
              </p>
              <div
                className="quiz-building-progress"
                role="progressbar"
                aria-label="Quiz preparation in progress"
                aria-valuetext="Preparing quiz"
              >
                <span />
              </div>
              <p className="quiz-building-caption">
                Your learning check-in is on its way
                <span className="quiz-building-ellipsis" aria-hidden="true">
                  …
                </span>
              </p>
            </section>
          ) : (
          <section className="quiz-container">
            <button
              type="button"
              className="lecture-back-button"
              onClick={() => {
                setQuizMode(false);
                setShowLectureFeedback(true);
                setQuizError("");
              }}
            >
              ← Back to lecture
            </button>

            <p className="page-label">CHECK YOUR UNDERSTANDING</p>
            <h1>{quiz?.title || "Your quiz"}</h1>

            {quizLoading && (
              <p className="lecture-status">Preparing your quiz…</p>
            )}

            {quizError && <p className="lecture-error">{quizError}</p>}

            {!quiz && !quizLoading && (
              <button
                type="button"
                className="lecture-action-button"
                onClick={startQuiz}
              >
                Generate quiz
              </button>
            )}

            {quiz && !quizResult && quiz.questions.length > 0 && (
              <section className="quiz-experience">
                {(() => {
                  const question = quiz.questions[quizQuestionIndex];
                  const selectedAnswer = quizAnswers[question.id];
                  const progress =
                    ((quizQuestionIndex + 1) / quiz.questions.length) * 100;

                  return (
                    <>
                      <div className="quiz-topbar">
                        <div>
                          <p className="page-label">{quiz.topic || topic}</p>
                          <span className="quiz-progress-text">
                            Question {quizQuestionIndex + 1} of{" "}
                            {quiz.questions.length}
                          </span>
                        </div>
                        <span className="quiz-difficulty">
                          {quiz.difficulty || difficultyLevel}
                        </span>
                      </div>

                      <div
                        className="quiz-progress-track"
                        role="progressbar"
                        aria-valuenow={Math.round(progress)}
                        aria-valuemin={0}
                        aria-valuemax={100}
                      >
                        <div
                          className="quiz-progress-fill"
                          style={{ width: `${progress}%` }}
                        />
                      </div>

                      <article className="quiz-question-card">
                        <p className="quiz-question-number">
                          {String(quizQuestionIndex + 1).padStart(2, "0")}
                        </p>
                        <h2>{question.question}</h2>

                        <div className="quiz-options">
                          {question.options.map((option, optionIndex) => (
                            <button
                              type="button"
                              key={option}
                              className={`quiz-answer-option ${
                                selectedAnswer === option ? "is-selected" : ""
                              }`}
                              aria-pressed={selectedAnswer === option}
                              onClick={() =>
                                chooseQuizAnswer(question.id, option)
                              }
                            >
                              <span>
                                {String.fromCharCode(65 + optionIndex)}
                              </span>
                              <strong>{option}</strong>
                            </button>
                          ))}
                        </div>
                      </article>

                      <div className="quiz-actions">
                        <button
                          type="button"
                          className="lecture-secondary-button"
                          disabled={quizLoading}
                          onClick={() => {
                            if (quizQuestionIndex === 0) {
                              setQuizMode(false);
                              setShowLectureFeedback(true);
                              return;
                            }
                            setQuizQuestionIndex((previous) => previous - 1);
                          }}
                        >
                          ← Back
                        </button>

                        <button
                          type="button"
                          className="lecture-action-button"
                          disabled={!selectedAnswer || quizLoading}
                          onClick={goToNextQuizQuestion}
                        >
                          {quizLoading
                            ? "Checking..."
                            : quizQuestionIndex === quiz.questions.length - 1
                              ? "Finish quiz"
                              : "Next question →"}
                        </button>
                      </div>
                    </>
                  );
                })()}
              </section>
            )}

            {quizResult && (
              <section className="quiz-result-card">
                <p className="page-label">YOUR LEARNING CHECK-IN</p>
                <h2>{quizResult.score}%</h2>
                <p className="quiz-result-summary">
                  You answered <strong>{quizResult.correct}</strong> of{" "}
                  <strong>{quizResult.total}</strong> questions correctly.
                </p>

                <p className="quiz-result-message">
                  {quizResult.score >= 80
                    ? "You have a strong understanding of this topic."
                    : quizResult.score >= 60
                      ? "You have a useful foundation. A little review will strengthen it."
                      : "This is a good signal to slow down and revisit the foundations."}
                </p>

                <div className="quiz-next-step">
                  <p className="page-label">RECOMMENDED NEXT STEP</p>
                  <p>{quizResult.next_step}</p>
                </div>

                {quizResult.results?.length > 0 && (
                  <section className="quiz-answer-review">
                    <h3>Review your answers</h3>
                    {quizResult.results.map((answerResult) => {
                      const question = quiz.questions.find(
                        (item) => item.id === answerResult.question_id,
                      );
                      return (
                        <article
                          key={answerResult.question_id}
                          className="quiz-review-item"
                        >
                          <h4>{question?.question || "Quiz question"}</h4>
                          <p>
                            Your answer: {answerResult.submitted_answer || "No answer"}
                          </p>
                          {!answerResult.correct && (
                            <p>
                              Correct answer: {answerResult.correct_answer}
                            </p>
                          )}
                          {answerResult.explanation && (
                            <p>{answerResult.explanation}</p>
                          )}
                        </article>
                      );
                    })}
                  </section>
                )}

                <div className="completion-actions">
                  <button
                    type="button"
                    className="lecture-action-button"
                    onClick={() => {
                      setQuizMode(false);
                      setQuiz(null);
                      setQuizResult(null);
                      setQuizAnswers({});
                      setQuizQuestionIndex(0);
                      setLectureFeedback("");
                      setShowLectureFeedback(false);
                      openHome();
                    }}
                  >
                    Return to learning space
                  </button>
                  <button
                    type="button"
                    className="lecture-secondary-button"
                    onClick={() => {
                      setQuizMode(false);
                      setQuiz(null);
                      setQuizResult(null);
                      setQuizAnswers({});
                      setQuizQuestionIndex(0);
                      openDashboard();
                    }}
                  >
                    View my dashboard
                  </button>
                </div>
              </section>
            )}
          </section>
          )}
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
                    showLectureFeedback ? (
                      <section className="completion-panel">
                        <p className="page-label">LECTURE COMPLETE</p>
                        <h2>You made it through this lesson.</h2>
                        <p>
                          Before checking your understanding, what stayed with
                          you from this lecture?
                        </p>
                        <textarea
                          value={lectureFeedback}
                          onChange={(event) =>
                            setLectureFeedback(event.target.value)
                          }
                          placeholder="Write one thing you understood, noticed, or still want to explore..."
                          rows={4}
                        />
                        <div className="completion-actions">
                          <button
                            type="button"
                            className="lecture-action-button"
                            onClick={continueToQuiz}
                          >
                            Continue to quiz
                          </button>
                          <button
                            type="button"
                            className="lecture-secondary-button"
                            onClick={() => {
                              setShowLectureFeedback(false);
                              openHome();
                            }}
                          >
                            Return to learning space
                          </button>
                        </div>
                      </section>
                    ) : (
                      <button
                        type="button"
                        className="lecture-action-button"
                        onClick={finishLecture}
                        disabled={completionLoading}
                      >
                        {completionLoading ? "Completing..." : "Complete lecture"}
                      </button>
                    )
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
              {completionError && (
                <p className="lecture-error">{completionError}</p>
              )}
            </>
          )}

          <section className="doubt-resolver">
            <p className="page-label">STILL CONFUSED?</p>
            <h2>Ask Novateach</h2>

            <form onSubmit={submitDoubt}>
              <textarea
                value={doubtText}
                onChange={(event) => setDoubtText(event.target.value)}
                placeholder="What part should we explain differently?"
                rows={4}
              />

              <button
                type="submit"
                className="lecture-secondary-button"
                disabled={doubtLoading}
              >
                {doubtLoading ? "Thinking..." : "Resolve my doubt"}
              </button>
            </form>

            {doubtError && <p className="lecture-error">{doubtError}</p>}

            {doubtResponse && (
              <div className="doubt-response">
                <h3>Explanation</h3>
                <p>{doubtResponse.answer}</p>
                <h3>In simpler words</h3>
                <p>{doubtResponse.simpler_explanation}</p>

                {doubtResponse.analogy && (
                  <>
                    <h3>Analogy</h3>
                    <p>{doubtResponse.analogy}</p>
                  </>
                )}

                {doubtResponse.next_question && (
                  <p className="page-objective">
                    Try this: {doubtResponse.next_question}
                  </p>
                )}
              </div>
            )}
          </section>
        </section>
      </main>
    );
  }

  if (currentView === "dashboard" && authenticatedUser) {
    return (
      <main className="dashboard-screen">
        <section className="dashboard-container">
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
              className="learning-home-explore"
              onClick={openHome}
            >
              Home
            </button>
          </header>

          <p className="learning-home-label">YOUR PROGRESS</p>
          <h1 className="learning-home-title">Your learning dashboard</h1>

          {dashboard?.profile && (
            <section className="dashboard-profile-card">
              <p className="page-label">YOUR LEARNING PROFILE</p>
              <h2>{dashboard.profile.name || authenticatedUser.name}</h2>
              <p>@{dashboard.profile.username || authenticatedUser.username}</p>
              <div className="profile-detail-grid">
                <div>
                  <span>UNDERSTANDING</span>
                  <strong>
                    {dashboard.profile.understanding_strategy || "Not set"}
                  </strong>
                </div>
                <div>
                  <span>SUPPORT</span>
                  <strong>
                    {dashboard.profile.support_strategy || "Not set"}
                  </strong>
                </div>
                <div>
                  <span>PACE</span>
                  <strong>
                    {dashboard.profile.pace_preference || "Not set"}
                  </strong>
                </div>
                <div>
                  <span>TEACHING FLOW</span>
                  <strong>
                    {dashboard.profile.teaching_strategy || "Not set"}
                  </strong>
                </div>
              </div>
            </section>
          )}

          <section className="dashboard-history dashboard-interests">
            <div className="dashboard-interests-heading">
              <div>
                <p className="page-label">YOUR INTERESTS</p>
                <h2>Topics to return to</h2>
              </div>
              <button
                type="button"
                className="dashboard-interest-browse"
                onClick={openExplore}
              >
                Browse Explore →
              </button>
            </div>
            {dashboard && dashboardError && (
              <p className="lecture-error">{dashboardError}</p>
            )}
            {savedExploreInterests.length === 0 ? (
              <p className="dashboard-interests-empty">
                Save a topic from Explore and it will be waiting for you here.
              </p>
            ) : (
              savedExploreInterests.map((interest) => (
                <article
                  className="dashboard-history-item dashboard-interest-item"
                  key={`${interest.subject}:${interest.topic}`}
                >
                  <div>
                    <strong>{interest.topic}</strong>
                    <span>
                      {interest.subject} ·{" "}
                      {interest.status === "later" ? "Learn later" : "Saved"}
                    </span>
                  </div>
                  <div className="dashboard-interest-actions">
                    <button
                      type="button"
                      className="dashboard-interest-learn"
                      onClick={() => {
                        setTopic(interest.topic);
                        openHome();
                      }}
                    >
                      Learn now
                    </button>
                    <button
                      type="button"
                      className="dashboard-interest-remove"
                      onClick={() =>
                        removeSavedExploreTopic(
                          interest.topic,
                          interest.subject,
                        )
                      }
                    >
                      Remove
                    </button>
                  </div>
                </article>
              ))
            )}
          </section>

          {dashboardLoading && (
            <p className="lecture-status">Loading your progress…</p>
          )}
          {dashboardError && !dashboard && (
            <p className="lecture-error">{dashboardError}</p>
          )}

          {dashboard && (
            <>
              <div className="dashboard-stats">
                <div className="dashboard-card">
                  <span>LECTURES STARTED</span>
                  <strong>{dashboard.stats.lectures_started}</strong>
                </div>
                <div className="dashboard-card">
                  <span>LECTURES COMPLETED</span>
                  <strong>{dashboard.stats.lectures_completed}</strong>
                </div>
                <div className="dashboard-card">
                  <span>QUIZZES</span>
                  <strong>{dashboard.stats.quizzes_completed}</strong>
                </div>
                <div className="dashboard-card">
                  <span>AVERAGE SCORE</span>
                  <strong>{dashboard.stats.average_score}%</strong>
                </div>
                <div className="dashboard-card">
                  <span>TOPICS STUDIED</span>
                  <strong>
                    {dashboard.stats.topics_studied ??
                      dashboard.stats.topics_completed}
                  </strong>
                </div>
              </div>

              <section className="dashboard-topic-insights">
                <article className="dashboard-next-step">
                  <p className="page-label">STRONGEST TOPICS</p>
                  {dashboard.strongest_topics?.length ? (
                    <ul className="dashboard-topic-list">
                      {dashboard.strongest_topics.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  ) : (
                    <p>Complete quizzes to identify your strongest topics.</p>
                  )}
                </article>
                <article className="dashboard-next-step">
                  <p className="page-label">TOPICS TO REVIEW</p>
                  {dashboard.topics_to_review?.length ? (
                    <ul className="dashboard-topic-list">
                      {dashboard.topics_to_review.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  ) : (
                    <p>No topics are currently flagged for review.</p>
                  )}
                </article>
              </section>

              <section className="dashboard-next-step">
                <p className="page-label">NEXT STEP</p>
                <p>{dashboard.next_step}</p>
              </section>

              <section className="dashboard-history">
                <p className="page-label">QUIZ HISTORY</p>
                {dashboard.quiz_history.length === 0 ? (
                  <p>Complete a quiz to see your progress here.</p>
                ) : (
                  dashboard.quiz_history.map((item) => (
                    <article
                      className="dashboard-history-item"
                      key={item.quiz_id}
                    >
                      <div>
                        <strong>{item.topic}</strong>
                        <span>{item.created_at}</span>
                        {item.feedback && <p>{item.feedback}</p>}
                      </div>
                      <strong>{item.score}%</strong>
                    </article>
                  ))
                )}
              </section>
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
            <button
              type="button"
              className="explore-header-button"
              onClick={openDashboard}
            >
              Progress
            </button>
          </header>

          {!explorePersonalized ? (
            <div className="explore-intro">
              <p className="explore-label">MAKE EXPLORE YOURS</p>

              <h1 className="explore-title">What are you curious about?</h1>

              <p className="explore-subtitle">
                Choose a few areas that genuinely interest you.
              </p>

              <p className="explore-selection-count" aria-live="polite">
                {selectedInterests.length === 0
                  ? "Select one or more subjects to shape your recommendations."
                  : `${selectedInterests.length} ${
                      selectedInterests.length === 1 ? "area" : "areas"
                    } selected`}
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
                    aria-pressed={selectedInterests.includes(interest)}
                  >
                    <span className="interest-marker" />
                    <span>{interest}</span>
                    <span className="interest-check" aria-hidden="true">
                      {selectedInterests.includes(interest) ? "Selected" : ""}
                    </span>
                  </button>
                ))}
              </div>

              <button
                type="button"
                className="explore-save-button"
                disabled={selectedInterests.length === 0}
                onClick={saveExploreInterests}
              >
                Show my subjects <span aria-hidden="true">→</span>
              </button>
              {exploreMessage && (
                <p className="lecture-error">{exploreMessage}</p>
              )}
            </div>
          ) : (
            <div className="explore-content">
              <div className="explore-heading-row">
                <div>
                  <p className="explore-label">YOUR LEARNING LIBRARY</p>
                  <h1 className="explore-title">Follow your curiosity.</h1>
                  <p className="explore-subtitle">
                    Browse a subject, find a question, and turn it into your next lesson.
                  </p>
                </div>
                <button
                  type="button"
                  className="explore-edit-button"
                  onClick={() => {
                    setExplorePersonalized(false);
                    setExploreSearch("");
                    setActiveExploreSubject("All areas");
                  }}
                >
                  Edit interests
                </button>
              </div>

              <label className="explore-search">
                <span className="explore-search-icon" aria-hidden="true">⌕</span>
                <span className="sr-only">Search subjects and topics</span>
                <input
                  type="search"
                  value={exploreSearch}
                  onChange={(event) => setExploreSearch(event.target.value)}
                  placeholder="Search topics, ideas, or subjects"
                />
                {exploreSearch && (
                  <button
                    type="button"
                    className="explore-search-clear"
                    onClick={() => setExploreSearch("")}
                    aria-label="Clear topic search"
                  >
                    Clear
                  </button>
                )}
              </label>

              <nav className="explore-subject-filters" aria-label="Filter by subject">
                {["All areas", ...personalizedSubjects.map((item) => item.name)].map(
                  (subjectName) => (
                    <button
                      key={subjectName}
                      type="button"
                      className={`explore-filter-button ${
                        activeExploreSubject === subjectName ? "is-active" : ""
                      }`}
                      aria-pressed={activeExploreSubject === subjectName}
                      onClick={() => setActiveExploreSubject(subjectName)}
                    >
                      {subjectName}
                    </button>
                  ),
                )}
              </nav>

              <div className="explore-results-heading" aria-live="polite">
                <span>
                  {exploreTopicCount}{" "}
                  {exploreTopicCount === 1 ? "topic" : "topics"} to explore
                </span>
                {exploreSearch && <span>Matching “{exploreSearch}”</span>}
              </div>

              {visibleExploreSubjects.length === 0 ? (
                <div className="explore-empty-state">
                  <span className="explore-empty-mark" aria-hidden="true">⌕</span>
                  <h2>No topics found</h2>
                  <p>Try a different search or browse all of your selected subjects.</p>
                  <button
                    type="button"
                    onClick={() => {
                      setExploreSearch("");
                      setActiveExploreSubject("All areas");
                    }}
                  >
                    Clear filters
                  </button>
                </div>
              ) : (
                <div className="explore-subject-list">
                  {visibleExploreSubjects.map((subject) => (
                    <section key={subject.id} className="explore-subject-section">
                      <div className="explore-subject-heading">
                        <span className="explore-subject-index">
                          {String(
                            personalizedSubjects.findIndex(
                              (item) => item.id === subject.id,
                            ) + 1,
                          ).padStart(2, "0")}
                        </span>
                        <div>
                          <h2>{subject.name}</h2>
                          <p>{subject.description}</p>
                        </div>
                        <span className="explore-subject-count">
                          {subject.topics.length}{" "}
                          {subject.topics.length === 1 ? "topic" : "topics"}
                        </span>
                      </div>

                      <div className="explore-topic-grid">
                        {subject.topics.map((subjectTopic) => (
                          <button
                            key={subjectTopic.name}
                            type="button"
                            className="explore-topic-card"
                            onClick={() => {
                              setSelectedExploreTopic({
                                topic: subjectTopic,
                                subject,
                              });
                              setExploreMessage("");
                            }}
                          >
                            <span className="explore-topic-name">
                              {subjectTopic.name}
                            </span>
                            {savedExploreInterests.some(
                              (interest) =>
                                interest.topic.toLowerCase() ===
                                  subjectTopic.name.toLowerCase() &&
                                interest.subject.toLowerCase() ===
                                  subject.name.toLowerCase(),
                            ) && (
                              <span className="explore-saved-mark">
                                {savedExploreInterests.find(
                                  (interest) =>
                                    interest.topic.toLowerCase() ===
                                      subjectTopic.name.toLowerCase() &&
                                    interest.subject.toLowerCase() ===
                                      subject.name.toLowerCase(),
                                )?.status === "later"
                                  ? "Learn later"
                                  : "In your interests"}
                              </span>
                            )}
                            <small className="explore-topic-description">
                              {subjectTopic.description}
                            </small>
                            <span className="explore-topic-cta">
                              Start learning <span aria-hidden="true">→</span>
                            </span>
                          </button>
                        ))}
                      </div>
                    </section>
                  ))}
                </div>
              )}
            </div>
          )}
          {selectedExploreTopic && (
            <div
              className="explore-topic-dialog-backdrop"
              onMouseDown={(event) => {
                if (event.target === event.currentTarget) {
                  setSelectedExploreTopic(null);
                }
              }}
            >
              <section
                className="explore-topic-dialog"
                role="dialog"
                aria-modal="true"
                aria-labelledby="explore-topic-dialog-title"
              >
                <button
                  type="button"
                  className="explore-topic-dialog-close"
                  aria-label="Close topic options"
                  onClick={() => setSelectedExploreTopic(null)}
                >
                  ×
                </button>
                <p className="explore-label">
                  {selectedExploreTopic.subject.name}
                </p>
                <h2 id="explore-topic-dialog-title">
                  {selectedExploreTopic.topic.name}
                </h2>
                <p>{selectedExploreTopic.topic.description}</p>
                <p className="explore-topic-dialog-question">
                  What would you like to do with this topic?
                </p>
                {exploreMessage && (
                  <p className="lecture-error">{exploreMessage}</p>
                )}
                <div className="explore-topic-dialog-actions">
                  <button
                    type="button"
                    className="explore-dialog-primary"
                    disabled={savingExploreInterest}
                    onClick={() => {
                      setTopic(selectedExploreTopic.topic.name);
                      setSelectedExploreTopic(null);
                      openHome();
                    }}
                  >
                    Learn this now
                  </button>
                  <button
                    type="button"
                    disabled={savingExploreInterest}
                    onClick={() => saveExploreTopic("saved")}
                  >
                    {savingExploreInterest
                      ? "Saving…"
                      : "Add to interests"}
                  </button>
                  <button
                    type="button"
                    disabled={savingExploreInterest}
                    onClick={() => saveExploreTopic("later")}
                  >
                    Learn later
                  </button>
                </div>
              </section>
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
            <button
              type="button"
              className="learning-home-explore"
              onClick={openDashboard}
            >
              Progress
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

export default App
