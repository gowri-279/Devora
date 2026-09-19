// Signal Garden style reminder: use asymmetric observability panels, seafoam progress signals, and quiet editorial hierarchy. Avoid generic centered dashboard grids.
import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  ArrowUpRight,
  BookOpen,
  BrainCircuit,
  Check,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  Code2,
  FileText,
  Github,
  LayoutDashboard,
  LockKeyhole,
  LogOut,
  Menu,
  MessageSquare,
  MoreHorizontal,
  Network,
  Search,
  Server,
  Settings2,
  ShieldCheck,
  Sparkles,
  Upload,
  Users,
  X,
  Zap,
} from "lucide-react";
import BobAssistant, { type BobReviewHandoff } from "@/components/BobAssistant";
import { toast } from "sonner";
import DeveloperTwin from "@/components/DeveloperTwin";
import TeamKnowledgeHeatmap from "@/components/TeamKnowledgeHeatmap";
import {
  defaultSkillProfile,
  heatmapRows,
  parseSkillProfile,
  personalizeModules,
  type HeatmapRow,
  type SkillProfile,
} from "@/lib/devoraMockData";
import {
  createAssessment,
  getLearningPath,
  generateModuleQuiz,
  checkModuleQuiz,
  getModuleProgress,
  submitAssessment as submitAssessmentApi,
  uploadRepository,
  uploadDocument,
  getProjectDocuments,
  getDeveloperTwin,
  createDeveloperTwinFromResume,
  getKnowledgeGaps,
  getNotifications,
  createNotification,
  resolveKnowledgeGap,
  getProjectRepository,
  type Assessment,
  type AssessmentResult,
  type LearningPathModule,
  type LearningPathResponse,
  type ProjectDocument,
} from "@/lib/devoraApi";

type Role = "developer" | "admin";
type View =
  | "dashboard"
  | "learning"
  | "documentation"
  | "notes"
  | "repository"
  | "members"
  | "twin"
  | "heatmap"
  | "gap-review";

const modules = [
  {
    title: "Project Overview",
    desc: "Learn the product vocabulary, team map, and the why behind the repository.",
    time: "12 min",
    status: "complete",
    tag: "01",
  },
  {
    title: "Local Setup",
    desc: "Get the project running locally and understand the environment contract.",
    time: "18 min",
    status: "current",
    tag: "02",
  },
  {
    title: "Architecture",
    desc: "Trace requests across the client, service layer, and Knowledge Engine.",
    time: "24 min",
    status: "locked",
    tag: "03",
  },
  {
    title: "APIs & Data Flow",
    desc: "Understand the integration points that power grounded onboarding.",
    time: "20 min",
    status: "locked",
    tag: "04",
  },
  {
    title: "Your first contribution",
    desc: "A project-specific path based on the role you are joining as.",
    time: "16 min",
    status: "locked",
    tag: "05",
  },
];

const members = [
  {
    name: "Maya Chen",
    role: "Frontend engineer",
    progress: 72,
    color: "#8cf7d0",
    initials: "MC",
  },
  {
    name: "Aarav Shah",
    role: "Backend engineer",
    progress: 48,
    color: "#9eaaff",
    initials: "AS",
  },
  {
    name: "Sofia Rossi",
    role: "Product engineer",
    progress: 31,
    color: "#f3b56b",
    initials: "SR",
  },
  {
    name: "Noah Williams",
    role: "New teammate",
    progress: 12,
    color: "#e8a2f7",
    initials: "NW",
  },
];

type Member = (typeof members)[number];

type GapNotification = {
  id: string;
  developer: string;
  question: string;
  uploadedContext: string;
  text: string;
};

const REVIEWED_GAPS_STORAGE_KEY = "devora-reviewed-knowledge-gaps";

function readReviewedGapIds() {
  if (typeof window === "undefined") return [];

  try {
    const parsed = JSON.parse(
      window.localStorage.getItem(REVIEWED_GAPS_STORAGE_KEY) ?? "[]",
    );

    return Array.isArray(parsed)
      ? parsed.filter(
          (value): value is string => typeof value === "string",
        )
      : [];
  } catch {
    return [];
  }
}

function writeReviewedGapIds(ids: string[]) {
  try {
    window.localStorage.setItem(
      REVIEWED_GAPS_STORAGE_KEY,
      JSON.stringify(Array.from(new Set(ids))),
    );
  } catch {
    /* localStorage may be unavailable in private browser contexts. */
  }
}

function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="brand-lockup">
      <div className="signal-mark">
        <span />
        <span />
        <span />
        <span />
      </div>

      {!compact && (
        <span className="wordmark">
          DEVOR<span className="wordmark-a">A</span>
        </span>
      )}
    </div>
  );
}

function Avatar({
  initials,
  color,
}: {
  initials: string;
  color: string;
}) {
  return (
    <div
      className="avatar"
      style={{
        background: `${color}1a`,
        color,
        borderColor: `${color}70`,
      }}
    >
      {initials}
    </div>
  );
}

function ProgressRing({ value }: { value: number }) {
  return (
    <div
      className="progress-ring"
      style={
        {
          "--progress": `${value * 3.6}deg`,
        } as React.CSSProperties
      }
    >
      <span>{value}%</span>
    </div>
  );
}

/*
 * The backend learning-path contract is intentionally different from the
 * frontend mock module shape. This adapter lets us use the real backend
 * learning path without rewriting the friend's existing UI components.
 */
type FrontendLearningPathModule = {
  title: string;
  desc: string;
  time: string;
  status: string;
  tag: string;
  reason: string;
  sources: string[];
  courseContent: NonNullable<
    LearningPathModule["course_content"]
  >;
};

function adaptLearningPath(
  backendModules: LearningPathModule[],
  completedModules: number[],
  selectedModule: number,
): FrontendLearningPathModule[] {
  return backendModules.map((module, index) => {
    const completed =
      completedModules.includes(index);

    return {
      title: module.title,
      desc: module.description,
      time: "20 min",
      status: completed
        ? "complete"
        : index === selectedModule
          ? "current"
          : index > selectedModule
            ? "locked"
            : "recommended",
      tag: String(module.step).padStart(2, "0"),
      reason: module.purpose,
      sources: module.sources ?? [],
      courseContent: module.course_content ?? [],
    };
  });
}

export default function Home() {
  const [role, setRole] = useState<Role | null>(null);
  const [authenticated, setAuthenticated] = useState(false);
  const [view, setView] = useState<View>("dashboard");
  const [mobileNav, setMobileNav] = useState(false);
  const [showProject, setShowProject] = useState(false);
  const [selectedModule, setSelectedModule] = useState(2);
  const [quizPassed, setQuizPassed] = useState(false);
  const [completedModules, setCompletedModules] = useState<number[]>([]);
  const completed = (moduleIndex: number) =>
  completedModules.includes(moduleIndex);
  const [quizAnswer, setQuizAnswer] = useState<string | null>(null);
  const [showHint, setShowHint] = useState(false);
  const [memberFocus, setMemberFocus] = useState(members[0]);
  const [projectOpen, setProjectOpen] = useState(false);
  const [activeProject, setActiveProject] =
  useState("FastAPI-101");
  const [activeProjectId, setActiveProjectId] = useState("fastapi-101");
  const [projectRepoUrl, setProjectRepoUrl] = useState<string | null>(null);
  const [bobQuizFeedback, setBobQuizFeedback] = useState<
    "idle" | "wrong" | "correct"
  >("idle");
  const [twinProfile, setTwinProfile] =
    useState<SkillProfile>(defaultSkillProfile);
  const [assessmentComplete, setAssessmentComplete] = useState(false);
  const [notesUnread, setNotesUnread] = useState(true);
  const [adminNotes, setAdminNotes] = useState<
    Array<{
      initials: string;
      color: string;
      name: string;
      role: string;
      time: string;
      text: string;
    }>
  >([]);
  const [memberProgress, setMemberProgress] = useState<
    Record<string, number>
  >({});
  const [teamHeatmapRows, setTeamHeatmapRows] =
    useState<HeatmapRow[]>(heatmapRows);
  const [gapNotifications, setGapNotifications] = useState<
    GapNotification[]
  >([]);
  const [bobHandoff, setBobHandoff] =
    useState<BobReviewHandoff | null>(null);

  /*
   * Real backend learning-path state.
   */
  const [backendLearningPath, setBackendLearningPath] =
    useState<LearningPathModule[] | null>(null);
  const [learningPathLoading, setLearningPathLoading] = useState(false);
  const [learningPathError, setLearningPathError] =
    useState<string | null>(null);

  /*
   * Use the real backend learning path whenever it has loaded.
   * Until then, preserve the existing mock path so the UI remains usable.
   */
  const modulePlan = backendLearningPath
   ? adaptLearningPath(
      backendLearningPath,
      completedModules,
      selectedModule,
    )
  : [];

  const currentModule =
    modulePlan[selectedModule] ?? modulePlan[0];

  const title = useMemo(
    () =>
      role === "admin"
        ? "Team Command Center"
        : "Your onboarding, in context",
    [role],
  );

  const enter = (nextRole: Role) => {
    setBobHandoff(null);
    setRole(nextRole);
    setAuthenticated(true);
    setView("dashboard");
  };

  const navigate = (nextView: View) => {
    setView(nextView);

    if (nextView !== "notes") {
      setBobHandoff(null);
    }
  };

  const logout = () => {
    setBobQuizFeedback("idle");
    setBobHandoff(null);
    setAuthenticated(false);
    setRole(null);
    setView("dashboard");
  };

  useEffect(() => {
    window.scrollTo(0, 0);

    if (view === "notes") {
      setNotesUnread(false);
    }
  }, [view]);

  useEffect(() => {
  if (!authenticated || role !== "developer") {
    return;
  }

  let cancelled = false;

  const loadDeveloperTwin = async () => {
    try {
      const result = await getDeveloperTwin(
        "dev-001",
        activeProjectId,
      );

      if (
        !cancelled &&
        result.status === "success" &&
        result.developer_twin
      ) {
        setTwinProfile((current) => ({
          ...current,
          skills: {
            APIs: result.developer_twin!.skills.apis,
            Architecture: result.developer_twin!.skills.architecture,
            Database: result.developer_twin!.skills.database,
            Security: result.developer_twin!.skills.security,
          },
        }));
        setAssessmentComplete(true);
        setTeamHeatmapRows((current) =>
          current.map((row) =>
            row.name === "Maya Chen"
              ? {
                ...row,
                scores: {
                  APIs: result.developer_twin!.skills.apis,
                  Architecture: result.developer_twin!.skills.architecture,
                  Database: result.developer_twin!.skills.database,
                  Security: result.developer_twin!.skills.security,
                },
                status: "Assessment analyzed",
                }
              : row,
          ),);
      }
      const gapResult = await getKnowledgeGaps(
        activeProjectId,
        1,
        "resolved",
      );
      const notificationResult = await getNotifications(
        "dev-001",
        "developer",
      );
      if (!cancelled) {
        setGapNotifications((current) => {
          const persisted = notificationResult.notifications.map(
            (notification) => ({
              id:
              notification.notification_id ??
              `${notification.gap_id}-${notification.created_at}`,
              developer: "Maya Chen",
              question: notification.question ?? "",
              uploadedContext: "",
              text: notification.text,
            }),
          );
          const existingIds = new Set(
            current.map((notification) => notification.id),
          );
          return [
            ...persisted.filter(
              (notification) => !existingIds.has(notification.id),
            ),
            ...current,
          ];
        });
      }
    } catch {
      // Keep the existing profile if the backend Twin is unavailable.
    }
  };

  void loadDeveloperTwin();

  return () => {
    cancelled = true;
  };
}, [authenticated, role, activeProjectId]);
  useEffect(() => {
  if (!authenticated || role !== "admin") {
    return;
  }

  let cancelled = false;

  const loadAdminNotifications = async () => {
    try {
      const result = await getNotifications(
        "admin-001",
        "admin",
      );

      if (!cancelled) {
        const notes = result.notifications.map(
          (notification) => {
            const date = new Date(
              notification.created_at,
            );

            return {
              initials: "DEV",
              color: "#f3b56b",
              name: "DEVORA",
              role: "Knowledge gap alert",
              time: date.toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              }),
              text: notification.text,
            };
          },
        );

        setAdminNotes(notes);
      }
    } catch {
      // Keep the existing Notes Feed if notifications are unavailable.
    }
  };

  void loadAdminNotifications();

  return () => {
    cancelled = true;
  };
}, [authenticated, role]);

  useEffect(() => {
  if (!authenticated || role !== "admin") {
    return;
  }

  let cancelled = false;

  const loadAdminHeatmap = async () => {
    try {
      console.log("ADMIN TWIN FETCH", {
        developerId: "dev-001",
        projectId: activeProjectId,
      });
      const result = await getDeveloperTwin(
        "dev-001",
        activeProjectId,
      );
      console.log("ADMIN TWIN RESULT", result.developer_twin);

      if (
        !cancelled &&
        result.status === "success" &&
        result.developer_twin
      ) {
        setTeamHeatmapRows((current) =>
          current.map((row) =>
            row.name === "Maya Chen"
              ? {
                  ...row,
                  scores: {
                    APIs: result.developer_twin!.skills.apis,
                    Architecture: result.developer_twin!.skills.architecture,
                    Database: result.developer_twin!.skills.database,
                    Security: result.developer_twin!.skills.security,
                  },
                  status: "Assessment analyzed",
                }
              : row,
          ),
        );
      }
    } catch {
      // Keep the existing heatmap if the backend Twin is unavailable.
    }
  };

  void loadAdminHeatmap();

  return () => {
    cancelled = true;
  };
}, [authenticated, role, activeProjectId]);

  /*
   * Load the real project-aware learning path once the developer enters
   * the workspace.
   */
  useEffect(() => {
    if (!authenticated || role !== "developer") {
      return;
    }

    let cancelled = false;

    const loadLearningPath = async () => {
      setLearningPathLoading(true);
      setLearningPathError(null);

      try {
        const result = await getLearningPath(
          "dev-001",
          activeProjectId,
        );

        if (!cancelled) {
  setBackendLearningPath(result.learning_path);

  // Reset learning-path state for the real backend course.
  // The original mock UI starts on module 2 with two completed
  // modules, which is not valid when the backend returns a
  // different number of modules.
  setSelectedModule(0);
  setCompletedModules([]);
  setQuizPassed(false);
}
      } catch (error) {
        if (!cancelled) {
          setLearningPathError(
            error instanceof Error
              ? error.message
              : "Failed to load learning path.",
          );
        }
      } finally {
        if (!cancelled) {
          setLearningPathLoading(false);
        }
      }
    };

    void loadLearningPath();

    return () => {
      cancelled = true;
    };
  },[authenticated, role, activeProjectId]);


  const submitAssessment = (result: AssessmentResult) => {
    const scores = {
      APIs: result.scores.APIs ?? 0,
      Architecture: result.scores.Architecture ?? 0,
      Database: result.scores.Database ?? 0,
      Security: result.scores.Security ?? 0,
    };

    setTwinProfile((current) => ({
      ...current,
      skills: scores,
    }));

    setTeamHeatmapRows((current) =>
      current.map((row) =>
        row.name === "Maya Chen"
          ? {
              ...row,
              scores,
              status: "Assessment analyzed",
            }
          : row,
      ),
    );

    setAssessmentComplete(true);
    setView("twin");
  };

  const notifyAdmin = () => {
    setMemberProgress((current) => ({
      ...current,
      "Maya Chen": 100,
    }));

    setAdminNotes((current) => [
      {
        initials: "MC",
        color: "#8cf7d0",
        name: "Maya Chen",
        role: "Frontend engineer",
        time: "Now",
        text: "Maya Chen completed onboarding and reached 100%.",
      },
      ...current,
    ]);

    toast.success(
      "Taylor has been notified that Maya reached 100%.",
    );
  };

  if (!authenticated) {
    return (
      <Landing
        role={role}
        setRole={setRole}
        onEnter={enter}
        onProfileCreate={setTwinProfile}
      />
    );
  }

  const navItems =
    role === "admin"
      ? [
          {
            key: "dashboard" as View,
            label: "Dashboard",
            Icon: LayoutDashboard,
          },
          {
            key: "heatmap" as View,
            label: "Knowledge heatmap",
            Icon: BrainCircuit,
          },
          {
            key: "repository" as View,
            label: "Repository",
            Icon: Code2,
          },
          {
            key: "documentation" as View,
            label: "Documentation",
            Icon: FileText,
          },
          {
            key: "members" as View,
            label: "Member status",
            Icon: Users,
          },
          {
            key: "notes" as View,
            label: "Notes Feed",
            Icon: MessageSquare,
          },
        ]
      : [
          {
            key: "dashboard" as View,
            label: "Dashboard",
            Icon: LayoutDashboard,
          },
          {
            key: "twin" as View,
            label: "Developer Twin",
            Icon: BrainCircuit,
          },
          {
            key: "learning" as View,
            label: "Learning path",
            Icon: BookOpen,
          },
          {
            key: "documentation" as View,
            label: "Documentation",
            Icon: FileText,
          },
          {
            key: "notes" as View,
            label: "Notes Feed",
            Icon: MessageSquare,
          },
        ];

  return (
    <div className="app-shell">
      <aside
        className={`side-rail ${
          mobileNav ? "mobile-open" : ""
        }`}
      >
        <div className="rail-top">
          <Logo />

          <button
            className="icon-btn mobile-only"
            onClick={() => setMobileNav(false)}
          >
            <X size={18} />
          </button>
        </div>

        <div className="rail-project-wrap">
          <button
            className={`rail-project ${
              projectOpen ? "open" : ""
            }`}
            onClick={() =>
              setProjectOpen((current) => !current)
            }
          >
            <div className="project-glyph">
              <Network size={16} />
            </div>

            <div>
              <small>ACTIVE PROJECT</small>
              <strong>{activeProject}</strong>
            </div>

            <ChevronDown size={14} />
          </button>

          {projectOpen && (
            <div className="project-menu">
              <button
                onClick={() => {
                  setActiveProject("FastAPI-101");
                  setActiveProjectId("fastapi-101");
                  setProjectOpen(false);
                }}
              >
                FastAPI-101 <span>active</span>
              </button>

              <button
                onClick={() => {
                  setActiveProject("Nimbus Portal");
                  setProjectOpen(false);
                }}
              >
                Project 2 <span>coming soon</span>
              </button>

              <button
                onClick={() => {
                  setActiveProject("Pulse Mobile");
                  setProjectOpen(false);
                }}
              >
                Project 3 <span>coming soon</span>
              </button>
            </div>
          )}
        </div>

        <nav className="rail-nav">
          {navItems.map(({ key, label, Icon }) => (
            <button
              key={key}
              className={view === key ? "active" : ""}
              onClick={() => {
                navigate(key);
                setMobileNav(false);
              }}
            >
              <Icon size={17} />
              <span>{label}</span>

              {key === "notes" && notesUnread && (
                <i className="unread-dot" />
              )}
            </button>
          ))}
        </nav>

        <div className="rail-bottom">
          <button className="logout" onClick={logout}>
            <LogOut size={17} />
            <span>Log out</span>
          </button>

          <div className="profile">
            <Avatar
              initials={role === "admin" ? "TS" : "MC"}
              color="#8cf7d0"
            />

            <div>
              <strong>
                {role === "admin"
                  ? "Taylor Swift"
                  : "Maya Chen"}
              </strong>

              <small>
                {role === "admin"
                  ? "Team Admin"
                  : "Frontend engineer"}
              </small>
            </div>
          </div>
        </div>
      </aside>

      <main className="workspace">
        <button
          className="mobile-nav-launcher mobile-only"
          onClick={() => setMobileNav(true)}
          aria-label="Open navigation"
        >
          <Menu size={20} />
        </button>

        <div className="page-content">
          {view === "dashboard" && (
            <Dashboard
              activeProject={activeProject}
              role={role!}
              modulePlan={modulePlan}
              title={title}
              onProject={() => setShowProject(true)}
              onView={navigate}
              onModule={() => navigate("learning")}
              onTwin={() => navigate("twin")}
              onHeatmap={() => navigate("heatmap")}
              onGapReview={() => navigate("gap-review")}
              onGapNote={(notification) => {
                setGapNotifications((current) => [
                  notification,
                  ...current,
                ]);
              }}
              onAdminMember={setMemberFocus}
            />
          )}

          {view === "learning" && (
            <LearningPath
              onAssessmentSubmit={submitAssessment}
              onNotifyAdmin={notifyAdmin}
              modulePlan={modulePlan}
              selectedModule={selectedModule}
              setSelectedModule={setSelectedModule}
              quizPassed={quizPassed}
              setQuizPassed={setQuizPassed}
              completedModules={completedModules}
              setCompletedModules={setCompletedModules}
              quizAnswer={quizAnswer}
              setQuizAnswer={setQuizAnswer}
              showHint={showHint}
              setShowHint={setShowHint}
              onBobFeedback={setBobQuizFeedback}
              learningPathLoading={learningPathLoading}
              learningPathError={learningPathError}
            />
          )}

          {view === "documentation" && (
            <Documentation
             role={role!}
             projectId="fastapi-101"
            />
          )}

          {view === "notes" && (
            <NotesFeed
              adminNotes={adminNotes}
              gapNotifications={gapNotifications}
              onViewAnswer={(notification) => {
                setBobHandoff({
                  id: notification.id,
                  question: notification.question,
                  uploadedContext:
                    notification.uploadedContext,
                });

                navigate("notes");
              }}
            />
          )}

          {view === "repository" && (
            <Repository
              projectId={activeProjectId}
              onConnected={(learningPath) => {
                setBackendLearningPath(learningPath.learning_path);
                setSelectedModule(0);
                setCompletedModules([]);
                setQuizPassed(false);
              }}
            />
          )}

          {view === "members" && (
            <MemberStatus
              focus={memberFocus}
              setFocus={setMemberFocus}
              memberProgress={memberProgress}
            />
          )}

          {view === "twin" && (
            <DeveloperTwin
              profile={twinProfile}
              assessmentComplete={assessmentComplete}
              onLearningPath={() => navigate("learning")}
            />
          )}

          {view === "gap-review" && (
            <KnowledgeGapReview
              onBack={() => navigate("dashboard")}
            />
          )}

          {view === "heatmap" && (
            <TeamKnowledgeHeatmap
              rows={teamHeatmapRows}
              onBack={() => navigate("dashboard")}
            />
          )}
        </div>
      </main>

      <BobAssistant
        projectId={activeProjectId}
        admin={role === "admin"}
        context={
          role === "admin"
            ? "Team Command Center"
            : currentModule?.title ?? "Project Overview"
        }
        quizFeedback={
          role === "admin" ? "idle" : bobQuizFeedback
        }
        reviewHandoff={bobHandoff}
      />

      {showProject && (
        <ProjectModal
          projectName={activeProject}
          onClose={() => setShowProject(false)}
        />
      )}
    </div>
  );
  useEffect(() => {
  if (!authenticated || role !== "developer") return;

  let cancelled = false;

  const loadProjectRepository = async () => {
    try {
      const result = await getProjectRepository(activeProjectId);

      if (!cancelled) {
        setProjectRepoUrl(result.repo_url);
      }
    } catch {
      if (!cancelled) {
        setProjectRepoUrl(null);
      }
    }
  };

  void loadProjectRepository();

  return () => {
    cancelled = true;
  };
}, [authenticated, role, activeProjectId]);
}

function Landing({
  role,
  setRole,
  onEnter,
  onProfileCreate,
}: {
  role: Role | null;
  setRole: (role: Role | null) => void;
  onEnter: (role: Role) => void;
  onProfileCreate: (profile: SkillProfile) => void;
}) {
  const [auth, setAuth] = useState(false);
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [passwordError, setPasswordError] = useState(false);
  const [profileFile, setProfileFile] =
    useState<File | null>(null);

  return (
    <div className="landing">
      <div className="landing-grid" />

      <header className="landing-nav">
        <Logo />
      </header>

      <div className="landing-main">
        <div className="landing-copy">
          {!role && (
            <>
              <p className="eyebrow">
                AI-POWERED DEVELOPER ONBOARDING
              </p>

              <h1>
                Turn unfamiliar
                <br />
                <em>code</em> into a
                <br />
                path forward.
              </h1>

              <p className="landing-lede">
                Devora understands your repository, maps the
                gaps, and gives every developer a clear way in.
              </p>

              <button
                className="primary-cta"
                onClick={() => setRole("developer")}
              >
                Meet Devora <ArrowUpRight size={17} />
              </button>
            </>
          )}

          {role && !auth && (
            <div className="role-chooser">
              <span>Who are you joining as?</span>

              <button
                onClick={() => setAuth(true)}
                className={
                  role === "developer" ? "selected" : ""
                }
              >
                Developer
              </button>

              <button
                onClick={() => {
                  setRole("admin");
                  setAuth(true);
                }}
                className={
                  role === "admin" ? "selected" : ""
                }
              >
                Team Admin
              </button>
            </div>
          )}

          {auth && (
            <form
              className="auth-card"
              onSubmit={(e) => {
                e.preventDefault();

                const expectedPassword =
                  role === "admin"
                    ? "admin123"
                    : "developer123";

                if (password !== expectedPassword) {
                  setPasswordError(true);
                  return;
                }

                setPasswordError(false);

                if (
                  (role ?? "developer") ===
                  "developer"
                ) {
                  const profile =
                    parseSkillProfile(
                      profileFile?.name ??
                        "skill-profile.pdf",
                      name || "Maya Chen",
                    );

                  onProfileCreate(profile);

                  if (profileFile) {
                    void createDeveloperTwinFromResume(
                      "dev-001",
                      "fastapi-101",
                      profileFile,
                    ).catch((error) => {
                      console.warn(
                        "Resume Twin upload failed; keeping local profile.",
                        error,
                      );
                    });
                  }
                }

                onEnter(role ?? "developer");
              }}
            >
              <div className="auth-head">
                <div>
                  <span className="eyebrow">
                    {role === "admin"
                      ? "TEAM ADMIN"
                      : "TEAM MEMBER"}
                  </span>

                  <h3>Welcome to Devora.</h3>
                </div>

                <button
                  type="button"
                  onClick={() => {
                    setAuth(false);
                    setRole(null);
                  }}
                >
                  <X size={17} />
                </button>
              </div>

              <label>
                Team ID
                <input
                  required
                  placeholder="atlas-core"
                />
              </label>

              <label>
                Your name
                <input
                  required
                  value={name}
                  onChange={(e) =>
                    setName(e.target.value)
                  }
                  placeholder={
                    role === "admin"
                      ? "Taylor Swift"
                      : "Maya Chen"
                  }
                />
              </label>

              {role === "developer" && (
                <label className="profile-upload">
                  <span>
                    Skill profile{" "}
                    <small>PDF, DOCX, JSON</small>
                  </span>

                  <input
                    type="file"
                    accept=".pdf,.doc,.docx,.json,.txt"
                    onChange={(e) =>
                      setProfileFile(
                        e.target.files?.[0] ?? null,
                      )
                    }
                  />

                  <strong>
                    {profileFile
                      ? profileFile.name
                      : "Upload your profile"}
                  </strong>
                </label>
              )}

              <label>
                Password
                <input
                  required
                  type="password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setPasswordError(false);
                  }}
                  placeholder={
                    role === "admin"
                      ? "admin123"
                      : "developer123"
                  }
                />

                {passwordError && (
                  <small className="auth-error">
                    Use the{" "}
                    {role === "admin"
                      ? "admin123"
                      : "developer123"}{" "}
                    demo password.
                  </small>
                )}
              </label>

              <button
                className="primary-cta"
                type="submit"
              >
                Enter workspace{" "}
                <ArrowUpRight size={16} />
              </button>

              <p className="auth-foot"></p>
            </form>
          )}
        </div>

        <div className="landing-visual">
          <div className="visual-orbit orbit-one" />
          <div className="visual-orbit orbit-two" />

          <div className="visual-caption">
            <span>DEVORA / 01</span>
            <small>YOUR OWN ONBOARDING PLATFORM</small>
          </div>

          <div className="instrument-panel panel-top">
            <span className="panel-line" />
            <b>REPOSITORY CONTEXT</b>
            <strong>YOUR PROJECT MAP</strong>
            <small>KNOWN BEFORE DAY ONE</small>
          </div>

          <div className="instrument-panel panel-bottom">
            <span className="panel-line" />
            <b>PATH PROGRESS</b>
            <strong>MODULE BY MODULE</strong>
            <small>GUIDED AROUND YOUR ROLE</small>
          </div>

          <div className="signal-core">
            <div className="core-label">KNOWLEDGE GAP</div>

            <div className="signal-core-mark">
              <span />
              <span />
              <span />
              <span />
            </div>

            <div className="core-readout">
              <span>FROM REPO TO READINESS</span>
              <b>START WITH CONTEXT</b>
            </div>
          </div>
        </div>
      </div>

      <footer className="landing-footer">
        <span>CtrlAltElite · 2026</span>
      </footer>
    </div>
  );
}

function Dashboard({
  activeProject,
  role,
  modulePlan,
  title,
  onProject,
  onView,
  onModule,
  onTwin,
  onHeatmap,
  onGapReview,
  onGapNote,
  onAdminMember,
}: {
  activeProject: string;
  role: Role;
  modulePlan: FrontendLearningPathModule[];
  title: string;
  onProject: () => void;
  onView: (view: View) => void;
  onModule: () => void;
  onTwin: () => void;
  onHeatmap: () => void;
  onGapReview: () => void;
  onGapNote: (notification: GapNotification) => void;
  onAdminMember: (member: Member) => void;
}) {
  const completedCount = modulePlan.filter(
    (module) => module.status === "complete",
  ).length;

  const completionPercent =
    modulePlan.length > 0
      ? Math.round(
          (completedCount / modulePlan.length) * 100,
        )
      : 0;

  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            {role === "admin"
  ? `TEAM OVERVIEW / ${new Date().toLocaleDateString(
      "en-US",
      {
        weekday: "long",
        month: "short",
        day: "numeric",
      },
    ).toUpperCase()}`
  : new Date()
      .toLocaleDateString("en-US", {
        weekday: "long",
        month: "long",
        day: "numeric",
        year: "numeric",
      })
      .toUpperCase()}
          </p>

          <h1>
            {role === "admin" ? (
              title
            ) : (
              <>
                Hi, Maya <span className="wave">✦</span>
              </>
            )}
          </h1>

          <p>
            {role === "admin"
            ? "A quiet view of where the team is moving, and where they might need help."
            : `You’re ${completionPercent}% through your onboarding path. Keep the signal moving.`}
          </p>
        </div>

        <div className="heading-actions">
          {role !== "admin" && (
            <button
              className="subtle-btn"
              onClick={onTwin}
            >
              <BrainCircuit size={16} />
              Developer Twin
              <ArrowUpRight size={14} />
            </button>
          )}

          <button
            className="subtle-btn"
            onClick={onProject}
          >
            <Network size={16} />
            Project details
            <ArrowUpRight size={14} />
          </button>
        </div>
      </div>

      {role === "admin" ? (
        <AdminDashboard
          activeProject={activeProject}
          onView={onView}
          onHeatmap={onHeatmap}
          onGapReview={onGapReview}
          onGapNote={onGapNote}
          onMember={onAdminMember}
        />
      ) : (
        <DeveloperDashboard
          modulePlan={modulePlan}
          onView={onView}
          onModule={onModule}
          onTwin={onTwin}
        />
      )}
    </>
  );
}

function DeveloperDashboard({
  modulePlan,
  onView,
  onModule,
  onTwin,
}: {
  modulePlan: FrontendLearningPathModule[];
  onView: (view: View) => void;
  onModule: () => void;
  onTwin: () => void;
}) {
  const [showPriorityActions, setShowPriorityActions] =
    useState(false);

  const [completedPriorityActions, setCompletedPriorityActions] =
    useState<boolean[]>([false, false, false]);

  const [projectRepoUrl, setProjectRepoUrl] =
  useState<string | null>(null);

  useEffect(() => {
  let cancelled = false;

  const loadProjectRepository = async () => {
    try {
      const result = await getProjectRepository("fastapi-101");

      if (!cancelled) {
        setProjectRepoUrl(result.repo_url);
      }
    } catch {
      if (!cancelled) {
        setProjectRepoUrl(null);
      }
    }
  };

  void loadProjectRepository();

  return () => {
    cancelled = true;
  };
}, []);

  const actions = [
    "Finish the Local Setup checkpoint.",
    "Review the API glossary with Bob.",
    "Complete the Architecture module questions.",
  ];

  const priorityActionsDone =
    completedPriorityActions.every(Boolean);

  return (
    <div className="dashboard-grid">
      <section className="primary-column">
        <div className="signal-card priority">
          <div className="card-top">
            <div>
              <span className="eyebrow seafoam">
                HIGHEST PRIORITY ACTION
              </span>

              <h2>
                {priorityActionsDone
                  ? "Youre done with the priority actions!"
                  : showPriorityActions
                    ? actions[1]
                    : actions[0]}
              </h2>
            </div>

            {!priorityActionsDone && (
              <button
                className={`round-btn ${
                  showPriorityActions ? "rotated" : ""
                }`}
                onClick={() =>
                  setShowPriorityActions(
                    (current) => !current,
                  )
                }
                aria-label="Show next priority actions"
              >
                <ChevronDown size={17} />
              </button>
            )}
          </div>

          <p>
            {priorityActionsDone
              ? "Your onboarding priorities are complete. Keep the context moving when you’re ready."
              : showPriorityActions
                ? "A clear next step for staying aligned with the team’s shared context."
                : "Complete the reading, then answer two questions so Bob can unlock Architecture."}
          </p>

          <div className="action-meta">
            <span>
              <Zap size={14} />
              {priorityActionsDone
                ? "All actions complete"
                : showPriorityActions
                  ? "22 min estimated"
                  : "18 min remaining"}
            </span>

            {!priorityActionsDone && (
              <button onClick={onModule}>
                {showPriorityActions
                  ? "Open learning path"
                  : "Continue module"}{" "}
                <ArrowUpRight size={14} />
              </button>
            )}
          </div>

          {(showPriorityActions ||
            priorityActionsDone) && (
            <div
              className={`priority-list ${
                priorityActionsDone ? "is-complete" : ""
              }`}
            >
              {actions.map((action, index) => (
                <div
                  className="priority-item"
                  key={action}
                >
                  <label
                    className="priority-check"
                    onClick={(event) =>
                      event.stopPropagation()
                    }
                  >
                    <input
                      type="checkbox"
                      checked={
                        completedPriorityActions[index]
                      }
                      onChange={(event) =>
                        setCompletedPriorityActions(
                          (current) =>
                            current.map(
                              (done, itemIndex) =>
                                itemIndex === index
                                  ? event.target.checked
                                  : done,
                            ),
                        )
                      }
                    />

                    <span className="priority-checkmark">
                      <Check size={12} />
                    </span>

                    <span className="sr-only">
                      Mark {action} as done
                    </span>
                  </label>

                  <button
                    className="priority-item-action"
                    onClick={() =>
                      index === 0
                        ? onModule()
                        : toast(
                            "This action will connect to your project feed.",
                          )
                    }
                  >
                    <span>
                      {String(index + 1).padStart(
                        2,
                        "0",
                      )}
                    </span>

                    <strong
                      className={
                        completedPriorityActions[index]
                          ? "is-done"
                          : ""
                      }
                    >
                      {action}
                    </strong>

                    <ChevronRight size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="section-head">
          <div>
            <span className="eyebrow">YOUR PATH</span>
            <h2>Keep the context flowing.</h2>
          </div>
        </div>

        <div className="path-preview">
          {modulePlan.slice(0, 3).map((module) => (
            <button
              key={module.title}
              onClick={onModule}
              className={`path-row ${module.status}`}
            >
              <span className="module-num">
                {module.status === "complete" ||
                module.status === "skipped" ? (
                  <Check size={15} />
                ) : module.status === "locked" ? (
                  <LockKeyhole size={14} />
                ) : (
                  module.tag
                )}
              </span>

              <span className="path-info">
                <strong>{module.title}</strong>
                <small>{module.desc}</small>
              </span>

              <span className="path-time">
                {module.time}
              </span>

              <ChevronRight size={16} />
            </button>
          ))}
        </div>
      </section>

      <aside className="secondary-column">
        <div className="mini-panel">
          <div className="section-head">
            <div>
              <span className="eyebrow">
                PROJECT RESOURCES
              </span>
              <h3>Everything in one place.</h3>
            </div>

            <MoreHorizontal size={17} />
          </div>

          <a
  className="resource-link"
  href={projectRepoUrl ?? "#"}
  target="_blank"
  rel="noreferrer"
  onClick={(event) => {
    if (!projectRepoUrl) {
      event.preventDefault();
    }
  }}
>
  <div className="resource-icon github">
    <Github size={17} />
  </div>

  <span>
    <strong>GitHub repository</strong>
    <small>
      {projectRepoUrl ?? "Repository not connected"}
    </small>
  </span>

  <ArrowUpRight size={15} />
</a>

          <button
            className="resource-link"
            onClick={() =>
              onView("documentation")
            }
          >
            <div className="resource-icon docs">
              <FileText size={17} />
            </div>

            <span>
              <strong>Company documentation</strong>
              <small>12 files · updated today</small>
            </span>

            <ArrowUpRight size={15} />
          </button>
        </div>

        <NotesPreview onView={onView} />
      </aside>
    </div>
  );
}

function NotesPreview({
  onView,
}: {
  onView: (view: View) => void;
}) {
  return (
    <div className="mini-panel notes-preview">
      <div className="section-head">
        <div>
          <span className="eyebrow">NOTES FEED</span>
          <h3>Team signal</h3>
        </div>

        <button
          className="text-btn"
          onClick={() => onView("notes")}
        >
          Open <ArrowUpRight size={13} />
        </button>
      </div>

      <div className="note-item">
        <Avatar initials="TS" color="#f3b56b" />

        <p>
          <strong>Taylor Swift</strong>
          <span>
            “API glossary is ready for review.”
          </span>
          <small>12 min ago</small>
        </p>
      </div>

      <div className="note-item">
        <Avatar initials="AS" color="#9eaaff" />

        <p>
          <strong>Aarav Shah</strong>
          <span>
            Moved into Architecture module.
          </span>
          <small>48 min ago</small>
        </p>
      </div>
    </div>
  );
}

function AdminDashboard({
  activeProject,
  onView,
  onHeatmap: _onHeatmap,
  onGapReview: _onGapReview,
  onGapNote,
  onMember,
}: {
  activeProject: string;
  onView: (view: View) => void;
  onHeatmap: () => void;
  onGapReview: () => void;
  onGapNote: (notification: GapNotification) => void;
  onMember: (member: typeof members[number]) => void;
}) {
  const isPlaceholderProject =
  activeProject === "Nimbus Portal" ||
  activeProject === "Pulse Mobile";
  return (
    <div className="admin-dashboard">
      <section className="admin-overview">
        <div className="team-orbit">
          <div
            className="team-orbit-graphics"
            aria-hidden="true"
          >
            <i className="orbit-ellipse ellipse-one" />
            <i className="orbit-ellipse ellipse-two" />
            <i className="orbit-ellipse ellipse-three" />
            <span className="orbit-spark spark-one" />
            <span className="orbit-spark spark-two" />
          </div>

          <div className="team-core">
            <Users size={22} />
            <strong>{isPlaceholderProject ? 0 : 4}</strong>
            <small>Team Members</small>
          </div>

          {!isPlaceholderProject &&
           members.map((member, index) => (
            <button
              key={member.name}
              className={`member-orbit orbit-${index + 1}`}
              onClick={() => onMember(member)}
            >
              <Avatar
                initials={member.initials}
                color={member.color}
              />
              <span>
                {member.name.split(" ")[0]}
              </span>
            </button>
          ))}
        </div>

        <div className="admin-kpis">
          <div>
            <span className="eyebrow">
              PATH COMPLETION
            </span>
            <strong>
              {isPlaceholderProject ? 0 : 41}
            </strong>
            <small>{isPlaceholderProject ? "No activity yet" : "+8% this week"}</small>
          </div>

          <div>
            <span className="eyebrow">
              KNOWLEDGE GAPS
            </span>
            <strong>{isPlaceholderProject ? "00" : "07"}</strong>
            <small className="amber-text">
              {isPlaceholderProject ? "No gaps yet" : "3 need review"}
            </small>
          </div>

          <div>
            <span className="eyebrow">
              ACTIVE TODAY
            </span>
            <strong>{isPlaceholderProject ? "00" : "03"}</strong>
            <small>{isPlaceholderProject ? "of 0 members" : "of 4 members"}</small>
          </div>
        </div>
      </section>

      {!isPlaceholderProject && (
  <KnowledgeGapReview
    inline
    onBack={() => onView("gap-review")}
    onGapNote={onGapNote}
  />
)}

      <NotesPreview onView={onView} />
    </div>
  );
}

function LearningPath({
  onAssessmentSubmit,
  onNotifyAdmin,
  modulePlan,
  selectedModule,
  setSelectedModule,
  quizPassed,
  setQuizPassed,
  completedModules,
  setCompletedModules,
  quizAnswer,
  setQuizAnswer,
  showHint,
  setShowHint,
  onBobFeedback,
  learningPathLoading,
  learningPathError,
}: {
  onAssessmentSubmit: (result: AssessmentResult) => void;
  onNotifyAdmin: () => void;
  modulePlan: FrontendLearningPathModule[];
  selectedModule: number;
  setSelectedModule: (value: number) => void;
  quizPassed: boolean;
  setQuizPassed: (value: boolean) => void;
  completedModules: number[];
  setCompletedModules: React.Dispatch<
    React.SetStateAction<number[]>
  >;
  quizAnswer: string | null;
  setQuizAnswer: (value: string | null) => void;
  showHint: boolean;
  setShowHint: (value: boolean) => void;
  onBobFeedback: (
    value: "idle" | "wrong" | "correct",
  ) => void;
  learningPathLoading: boolean;
  learningPathError: string | null;
}) {
  const completed = (moduleIndex: number) =>
      completedModules.includes(moduleIndex);
  const locked = (moduleIndex: number) =>
  moduleIndex > 0 &&
  !completedModules.includes(moduleIndex - 1);
  const [started, setStarted] = useState(false);
  const [activeQuestion, setActiveQuestion] =
    useState(0);
  const [answers, setAnswers] =
  useState<Record<number, number>>({});
  const [moduleQuiz, setModuleQuiz] = useState<
  Array<{
    question_id: string;
    question: string;
    options: string[];
  }>
>([]);
  const [quizLoading, setQuizLoading] = useState(false);
  const [notes, setNotes] = useState("");
  const [assessmentAnswers, setAssessmentAnswers] =
    useState<Record<string, string>>({});
  const [journeyComplete, setJourneyComplete] =
    useState(false);
  const [completionReady, setCompletionReady] =
    useState(false);
  const [adminNotified, setAdminNotified] =
    useState(false);

  const [backendAssessment, setBackendAssessment] =
    useState<Assessment | null>(null);
  const [assessmentLoading, setAssessmentLoading] =
    useState(false);
  const [assessmentSubmitting, setAssessmentSubmitting] =
    useState(false);
  const [assessmentError, setAssessmentError] =
    useState<string | null>(null);

  const mod =
  modulePlan[selectedModule] ??
  modulePlan[0] ?? {
    title: "Loading learning path...",
    desc: "Devora is loading your project-aware learning path.",
    time: "20 min",
    status: "current",
    tag: "01",
    reason: "Preparing your learning path from the project knowledge base.",
    sources: [],
    courseContent: [],
  };

  const progressPercent =
    modulePlan.length === 0
      ? 0
      : Math.round(
          (completedModules.length /
            modulePlan.length) *
            100,
        );

  const questionSets = [
    [
      {
        prompt:
          "Which project map should you read first?",
        options: [
          "Project Overview",
          "package.json",
          "git log",
          "node_modules",
        ],
        correct: "Project Overview",
        explanation:
          "The overview anchors the vocabulary that makes every later module easier to follow.",
      },
      {
        prompt:
          "What does Devora connect to build a learning path?",
        options: [
          "Only tickets",
          "Repository and company context",
          "Only chat history",
          "A random sample",
        ],
        correct:
          "Repository and company context",
        explanation:
          "Devora combines repository signals with team documentation to shape the route.",
      },
    ],
    [
      {
        prompt:
          "Which command installs the project dependencies?",
        options: [
          "npm start",
          "pnpm install",
          "git pull",
          "node setup.js",
        ],
        correct: "pnpm install",
        explanation:
          "pnpm install keeps the dependency graph reproducible across the team.",
      },
      {
        prompt:
          "Where should local environment values live?",
        options: [
          "README.md",
          ".env.local",
          "package.json",
          "src/index.ts",
        ],
        correct: ".env.local",
        explanation:
          "The local environment file keeps machine-specific values out of the shared source.",
      },
    ],
    [
      {
        prompt:
          "What should you trace first in an unfamiliar request?",
        options: [
          "The browser tab",
          "The client entry and service boundary",
          "The lockfile only",
          "A random component",
        ],
        correct:
          "The client entry and service boundary",
        explanation:
          "Architecture becomes legible when the request path is followed from the client into the service layer.",
      },
      {
        prompt: "What makes a boundary useful?",
        options: [
          "It hides every detail",
          "It clarifies ownership and flow",
          "It removes documentation",
          "It changes on every request",
        ],
        correct:
          "It clarifies ownership and flow",
        explanation:
          "Clear boundaries help the team reason about ownership, behavior, and change.",
      },
    ],
    [
      {
        prompt:
          "What keeps an API handoff grounded?",
        options: [
          "A shared contract",
          "A hidden endpoint",
          "A screenshot",
          "An unrelated ticket",
        ],
        correct: "A shared contract",
        explanation:
          "Shared contracts make integration points and data movement predictable.",
      },
      {
        prompt:
          "What should you inspect when data looks wrong?",
        options: [
          "The full path from request to response",
          "Only the button color",
          "The footer",
          "A different project",
        ],
        correct:
          "The full path from request to response",
        explanation:
          "Following the full path surfaces where a transformation or contract drift occurred.",
      },
    ],
    [
      {
        prompt:
          "Which practice protects authentication context?",
        options: [
          "Keep secrets in source",
          "Validate and scope session context",
          "Share one global token",
          "Skip persistence rules",
        ],
        correct:
          "Validate and scope session context",
        explanation:
          "Scoped, validated context keeps authentication and persistence boundaries predictable.",
      },
      {
        prompt:
          "What makes a final change safe to ship?",
        options: [
          "No review",
          "A verified flow and clear rollback",
          "A louder alert",
          "Deleting the docs",
        ],
        correct:
          "A verified flow and clear rollback",
        explanation:
          "Confidence comes from a tested path, understandable ownership, and a safe recovery plan.",
      },
    ],
  ];

  const questions =
  questionSets[selectedModule] ??
  questionSets[questionSets.length - 1] ??
  [];

  const question = questions[activeQuestion];
  

  const triggerBob = (
    feedback: "wrong" | "correct",
  ) => {
    onBobFeedback("idle");

    window.setTimeout(
      () => onBobFeedback(feedback),
      20,
    );
  };

  const choose = (answer: string) => {
  const optionIndex = question.options.indexOf(answer);

  setAnswers((current) => ({
    ...current,
    [activeQuestion]: optionIndex,
  }));

  setQuizAnswer(answer);

  const isCorrect = answer === question.correct;

  if (isCorrect) {
    triggerBob("correct");
  } else {
    triggerBob("wrong");
  }

  if (isCorrect && activeQuestion < questions.length - 1) {
    window.setTimeout(() => {
      setActiveQuestion((current) => current + 1);
      setQuizAnswer(null);
    }, 300);

    return;
  }

  if (isCorrect) {
    setQuizPassed(true);

    const isFinalModule =
      selectedModule === modulePlan.length - 1;

    setCompletionReady(isFinalModule);
    setJourneyComplete(isFinalModule);

    setCompletedModules((current) =>
      current.includes(selectedModule)
        ? current
        : [...current, selectedModule],
    );
  } else {
    setQuizPassed(false);
    setShowHint(false);
  }
};

    useEffect(() => {
    if (
      !journeyComplete ||
      selectedModule !== modulePlan.length - 1 ||
      backendAssessment ||
      assessmentLoading
    ) {
      return;
    }

    const loadAssessment = async () => {
      setAssessmentLoading(true);
      setAssessmentError(null);

      try {
        const result = await createAssessment(
          "dev-001",
          "fastapi-101",
        );

        setBackendAssessment(result);
      } catch (error) {
        setAssessmentError(
          error instanceof Error
            ? error.message
            : "Unable to prepare assessment.",
        );
      } finally {
        setAssessmentLoading(false);
      }
    };

    void loadAssessment();
  }, [
    journeyComplete,
    selectedModule,
    modulePlan.length,
    backendAssessment,
    assessmentLoading,
  ]);

  const moduleBody = !started ? (
    <>
      <div className="module-detail-head">
        <div>
          <span className="eyebrow seafoam">
            MODULE {mod.tag} /{" "}
            {completedModules.includes(selectedModule)
              ? "COMPLETE"
              : "READY"}
          </span>

          <h2>{mod.title}</h2>
          <p>{mod.desc}</p>
        </div>

        <div className="module-time">
          <Zap size={15} /> {mod.time}
        </div>
      </div>

      <div className="module-progress">
        <span
          style={{
            width: completedModules.includes(selectedModule)
              ? "100%"
              : "62%",
          }}
        />
      </div>

      <div className="module-summary">
        <span className="summary-mark">
          <BookOpen size={20} />
        </span>

        <div>
          <span className="eyebrow">
            MODULE SUMMARY
          </span>

          <h3>
            {selectedModule === 1
              ? "A calm first step into the codebase."
              : "Build the context you need."}
          </h3>

          <p>
            {selectedModule === 1
              ? "Learn the environment contract, the commands the team trusts, and how to verify a clean local session before touching product logic."
              : mod.desc}
          </p>

          <div className="summary-meta">
            <span>
              <Zap size={14} /> {mod.time}
            </span>

            <span>
              <CircleHelp size={14} />{" "}
              {selectedModule === 1
                ? "2 questions"
                : "Reading + checkpoint"}
            </span>
          </div>

          <button
  className="primary-cta"
  onClick={async () => {
    setQuizLoading(true);
    setQuizPassed(false);
    setActiveQuestion(0);
    setQuizAnswer(null);
    setAnswers({});

    setStarted(true);
    setQuizLoading(false);
  }}
>
  {completedModules.includes(selectedModule)
    ? "Review module"
    : "Start module"}{" "}
  <ArrowUpRight size={15} />
</button>
        </div>
      </div>
    </>
  ) : (
    <div className="module-reading-wrap">
      <div className="module-reading">
        <div className="reading-toolbar">
          <button
            className="text-btn"
            onClick={() => setStarted(false)}
          >
            <ChevronRight
              size={14}
              className="back-chevron"
            />{" "}
            Return to Learning path
          </button>

          <span className="eyebrow">
            MODULE {mod.tag} / READING MODE
          </span>
        </div>

        <div className="module-reading-head">
          <span className="eyebrow seafoam">
            ATLAS CORE / LOCAL SETUP
          </span>

          <h2>{mod.title}</h2>
          <p>
            Make the first local run feel predictable.
          </p>
        </div>

        <div className="reading-copy">
          {mod.courseContent && mod.courseContent.length > 0 ? (
    <>
      <p className="lead">
        {mod.reason || mod.desc}
      </p>

      {mod.courseContent.map((source, index) => (
  <div
    key={`${source.source_file}-${index}`}
    className="course-content-source"
  >
    <p className="eyebrow">
      {source.scope || "PROJECT SOURCE"}
    </p>

    <h3>{source.filename}</h3>

    <pre className="course-content">
      {source.content}
    </pre>
  </div>
))}
    </>
  ) : (
    <>
      <p className="lead">
        {mod.desc}
      </p>

      <p>
        This module is based on the project
        context identified by Devora. Source
        content will appear here when available.
      </p>
    </>
  )}
</div>

        <div className="quiz-card">
          <div className="quiz-title">
            <span className="eyebrow">
              CHECKPOINT / 0{activeQuestion + 1} OF 02
            </span>

            <h3>{question.prompt}</h3>
          </div>

          <div className="quiz-options">
            {question.options.map((answer) => (
              <button
                key={answer}
                className={
  quizAnswer === answer
    ? answer === question.correct
      ? "selected correct"
      : "selected wrong"
    : ""
}
                onClick={() => choose(answer)}
              >
                {answer}

                <span>
                  {answers[activeQuestion] ===
                   question.options.indexOf(answer) && (
                   <Check size={15} />
                  )}
                </span>
              </button>
            ))}
          </div>

          {completionReady &&
            selectedModule ===
              modulePlan.length - 1 && (
              <button
                className="primary-cta next-module-btn"
                onClick={async () => {
                  setCompletedModules((current) =>
                    current.includes(selectedModule)
                  ? current
                  : [...current, selectedModule],
                );
                setJourneyComplete(true);
                setCompletionReady(false);
                try {
                  await createNotification({
                    recipientId: "dev-001",
                    role: "developer",
                    text: "Onboarding journey completed.",
                    question: "You completed the full onboarding learning path.",
                  });
                } catch {
    // Keep completion successful even if notification storage fails.
    }
  }}
              >
                MARK COMPLETE <Check size={15} />
              </button>
            )}

          {quizPassed &&
            selectedModule <
              modulePlan.length - 1 && (
              <button
                className="primary-cta next-module-btn"
                onClick={() => {
                  setStarted(false);

                  setSelectedModule(
                    Math.min(
                      selectedModule + 1,
                      modulePlan.length - 1,
                    ),
                  );

                  setQuizAnswer(null);
                  setShowHint(false);
                  setQuizPassed(false);
                  setJourneyComplete(false);
                  setCompletionReady(false);
                  setAdminNotified(false);
                  setActiveQuestion(0);
                  setAnswers({});
                }}
              >
                Start next module{" "}
                <ArrowUpRight size={15} />
              </button>
            )}
        </div>
      </div>
    </div>
  );

  const completionBody =
    journeyComplete &&
    selectedModule === modulePlan.length - 1 ? (
      <div className="completion-summary">
        <div className="completion-badge">
          <Sparkles size={18} />
          <span>PATH COMPLETE</span>
        </div>

        <h2>CONGRATULATIONS ON YOUR ONBOARDING!</h2>

        <p>Here is a summary of your journey:</p>

        <div className="completion-modules">
          {modulePlan.map((item) => (
            <div key={item.title}>
              <span>
                <Check size={14} />
              </span>

              <strong>{item.title}</strong>
              <small>{item.desc}</small>
            </div>
          ))}
        </div>

        <div className="completion-footer">
          <p>
            You mapped the product, made the environment
            predictable, traced the architecture, followed
            the data flow, and finished with security
            context. Bob now has the full signal.
          </p>

          <button
            className="primary-cta"
            onClick={() => {
              onNotifyAdmin();
              setAdminNotified(true);
            }}
          >
            {adminNotified
              ? "Admin notified"
              : "Notify admin"}{" "}
            <ArrowUpRight size={15} />
          </button>
        </div>

        <div className="completion-assessment">
          <div className="completion-assessment-heading">
            <span className="eyebrow seafoam">
              FINAL KNOWLEDGE ASSESSMENT / 05 QUESTIONS
            </span>

            <h3>
              Now show how you apply the context.
            </h3>

            <p>
              This assessment appears once, at the end
              of your onboarding. Bob will use your five
              application-based answers to update the
              four-area knowledge heatmap.
            </p>
          </div>

          {assessmentLoading && (
            <div className="assessment-shell">
              <div className="assessment-intro">
                <span className="eyebrow seafoam">
                  PREPARING ASSESSMENT
                </span>

                <h2>
                  Loading your project-aware
                  questions.
                </h2>

                <p>
                  Devora is preparing the assessment
                  from the connected backend.
                </p>
              </div>
            </div>
          )}

          {assessmentError && (
            <div className="assessment-shell">
              <div className="assessment-intro">
                <span className="eyebrow amber-text">
                  ASSESSMENT UNAVAILABLE
                </span>

                <h2>
                  We could not prepare the
                  assessment.
                </h2>

                <p>{assessmentError}</p>

                <button
                  className="primary-cta"
                  onClick={() => {
                    setBackendAssessment(null);
                    setAssessmentError(null);
                  }}
                >
                  Try again{" "}
                  <ArrowUpRight size={15} />
                </button>
              </div>
            </div>
          )}

          {backendAssessment &&
            !assessmentLoading && (
              <AssessmentPanel
                questions={backendAssessment.questions}
                answers={assessmentAnswers}
                setAnswers={setAssessmentAnswers}
                onSubmit={async (answers) => {
  setAssessmentSubmitting(true);

  try {
    const result = await submitAssessmentApi(
      backendAssessment!.assessment_id,
      "dev-001",
      backendAssessment!.questions.map((question) => ({
        question_id: question.question_id,
        answer: answers[question.question_id] ?? "",
      })),
    );

    onAssessmentSubmit(result);
  } catch (error) {
    setAssessmentError(
      error instanceof Error
        ? error.message
        : "Unable to submit assessment.",
    );
  } finally {
    setAssessmentSubmitting(false);
  }
}}
                submitting={assessmentSubmitting}
              />
            )}
        </div>
      </div>
    ) : (
      moduleBody
    );

  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            ONBOARDING / {progressPercent}% COMPLETE
          </p>

          <h1>Learning path</h1>

          <p>
            A guided route through the parts of Atlas Core
            that matter most to your role.
          </p>

          {learningPathLoading && (
            <small>
              Loading your project-aware learning path…
            </small>
          )}

          {learningPathError &&
            !learningPathLoading && (
              <small>
                Using the local learning path while the
                backend path is unavailable.
              </small>
            )}
        </div>

        <div className="progress-summary">
          <ProgressRing value={progressPercent} />

          <span>
            <strong>
              {completedModules.length} of{" "}
              {modulePlan.length}
            </strong>

            <small>modules completed</small>
          </span>
        </div>
      </div>

      <div
        className={`learning-layout ${
          started ? "is-reading" : ""
        } ${journeyComplete ? "is-complete" : ""}`}
      >
        <div className="module-list">
          <div className="eyebrow">YOUR MODULES</div>

          {modulePlan.map((item, index) => (
            <button
              key={item.title}
              className={`module-item ${
                index === selectedModule
                  ? "selected"
                  : ""
              } ${locked(index) ? "locked" : ""}`}
              onClick={() => {
                if (!locked(index)) {
                  setSelectedModule(index);
                  setStarted(false);
                  setQuizPassed(completed(index));
                  setJourneyComplete(false);
                  setCompletionReady(false);
                  setAdminNotified(false);
                  setActiveQuestion(0);
                  setQuizAnswer(null);
                }
              }}
            >
              <span className="module-num">
                {completed(index) ? (
                  <Check size={14} />
                ) : locked(index) ? (
                  <LockKeyhole size={13} />
                ) : (
                  item.tag
                )}
              </span>

              <span>
                <strong>{item.title}</strong>

                <small>
                  {item.time} ·{" "}
                  {completed(index)
                    ? "Completed"
                    : locked(index)
                      ? "Locked"
                      : index === selectedModule &&
                          started
                        ? "In progress"
                        : "Ready to start"}
                </small>
              </span>

              <ChevronRight size={15} />
            </button>
          ))}
        </div>

        <section className="module-detail">
          {completionBody}
        </section>

        {started && !journeyComplete && (
          <aside className="module-notes">
            <div className="section-head">
              <div>
                <span className="eyebrow">
                  PRIVATE NOTES
                </span>

                <h3>Keep a thought here.</h3>
              </div>

              <MoreHorizontal size={17} />
            </div>

            <textarea
              value={notes}
              onChange={(event) =>
                setNotes(event.target.value)
              }
              placeholder="Write anything you want to remember..."
            />
          </aside>
        )}
      </div>
    </>
  );
}

function AssessmentPanel({
  questions,
  answers,
  setAnswers,
  onSubmit,
  submitting,
}: {
  questions: Assessment["questions"];
  answers: Record<string, string>;
  setAnswers: React.Dispatch<
    React.SetStateAction<Record<string, string>>
  >;
  onSubmit: (answers: Record<string, string>) => void;
  submitting: boolean;
}) {
  const complete =
    questions.length === 5 &&
    questions.every(
      (question) =>
        (
          answers[question.question_id] ?? ""
        ).trim().length > 0,
    );

  const answeredCount = questions.filter(
    (question) =>
      (
        answers[question.question_id] ?? ""
      ).trim().length > 0,
  ).length;

  return (
    <div className="assessment-shell">
      <div className="assessment-intro">
        <span className="eyebrow seafoam">
          BOB’S OPEN-ENDED READ / 05 QUESTIONS
        </span>

        <h2>
          Show your thinking, not your memorization.
        </h2>

        <p>
          Answer exactly five descriptive prompts in
          your own words. Bob will use the responses to
          update your Developer Twin after the final
          module.
        </p>

        <div className="assessment-status">
          <span>
            <BrainCircuit size={15} /> {answeredCount} of{" "}
            {questions.length} answered
          </span>

          <span>Private to your Twin</span>
        </div>
      </div>

      <div className="assessment-list">
        {questions.map((question, index) => (
          <label
            className="assessment-question"
            key={question.question_id}
          >
            <span>
              <b>
                {String(index + 1).padStart(2, "0")}
              </b>

              {question.question}
            </span>

            <textarea
              value={
                answers[question.question_id] ?? ""
              }
              onChange={(event) =>
                setAnswers((current) => ({
                  ...current,
                  [question.question_id]:
                    event.target.value,
                }))
              }
              placeholder="Write a short explanation..."
              disabled={submitting}
            />
          </label>
        ))}

        <div className="assessment-actions">
          <button
            className="primary-cta"
            disabled={!complete || submitting}
            onClick={() => onSubmit(answers)}
          >
            {submitting
              ? "Analyzing with Bob..."
              : complete
                ? "Analyze with Bob"
                : `Answer ${
                    5 - answeredCount
                  } more`}

            <ArrowUpRight size={15} />
          </button>
        </div>
      </div>
    </div>
  );
}

function Documentation({
  role,
  projectId,
}: {
  role: Role;
  projectId: string;
}) {
  const [documents, setDocuments] = useState<
    ProjectDocument[]
  >([]);

  const [selected, setSelected] =
    useState<ProjectDocument | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [uploading, setUploading] =
    useState(false);

  const fileInputRef =
    useRef<HTMLInputElement>(null);

  const loadDocuments = async () => {
    if (!projectId) {
      setDocuments([]);
      setSelected(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);

      const result =
        await getProjectDocuments(projectId);

      /*
       * raw_documents contains both repository source files
       * and uploaded project documents.
       *
       * The Documentation screen should show documentation
       * files rather than every repository source file.
       */
      const documentationFiles =
        result.documents.filter((document) => {
          const filename =
            document.source_file
              .split("/")
              .pop()
              ?.toLowerCase() ?? "";

          return [
            ".pdf",
            ".doc",
            ".docx",
            ".txt",
            ".md",
            ".rst",
          ].some((extension) =>
            filename.endsWith(extension),
          );
        });

      setDocuments(documentationFiles);

      setSelected((current) => {
        if (!documentationFiles.length) {
          return null;
        }

        if (!current) {
          return documentationFiles[0];
        }

        return (
          documentationFiles.find(
            (document) =>
              document.source_file ===
              current.source_file,
          ) ?? documentationFiles[0]
        );
      });
    } catch (error) {
      console.error(
        ">>> PROJECT DOCUMENTS LOAD FAILED:",
        error,
      );

      toast.error(
        error instanceof Error
          ? error.message
          : "Unable to load project documentation.",
      );

      setDocuments([]);
      setSelected(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadDocuments();
  }, [projectId]);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleDocumentSelection = async (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (!projectId) {
      toast.error("No active project is selected.");
      event.target.value = "";
      return;
    }

    setUploading(true);

    try {
      const result = await uploadDocument(
        projectId,
        file,
      );

      console.log(
        ">>> PROJECT DOCUMENT INGESTED:",
        result,
      );

      toast.success(
        `${file.name} added to project knowledge.`,
      );

      /*
       * Reload the real document list so the newly uploaded
       * document immediately appears in the Documentation UI.
       */
      await loadDocuments();
    } catch (error) {
      toast.error(
        error instanceof Error
          ? error.message
          : "Unable to upload project document.",
      );
    } finally {
      setUploading(false);

      // Allow selecting the same file again later.
      event.target.value = "";
    }
  };

  const selectedFilename =
    selected?.source_file
      .split("/")
      .pop() ?? "Documentation";

  const selectedExtension =
    selectedFilename.includes(".")
      ? selectedFilename
          .split(".")
          .pop()
          ?.toUpperCase()
      : "DOCUMENT";

  const updatedLabel = selected?.updated_at
    ? new Date(
        selected.updated_at,
      ).toLocaleString()
    : "Recently updated";

  const documentLines =
    selected?.text
      .split(/\n+/)
      .map((line) => line.trim())
      .filter(Boolean) ?? [];

  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            KNOWLEDGE BASE /{" "}
            {role === "admin"
              ? "ADMIN UPLOADS"
              : `${documents.length} FILE${
                  documents.length === 1
                    ? ""
                    : "S"
                }`}
          </p>

          <h1>Documentation</h1>

          <p>
            {role === "admin"
              ? "Give the Knowledge Engine the context your team needs."
              : "A project-aware file viewer for the context behind the code."}
          </p>
        </div>

        {role === "admin" && (
          <>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.doc,.docx,.md,.txt,.rst"
              onChange={handleDocumentSelection}
              style={{ display: "none" }}
            />

            <button
              className="primary-cta"
              onClick={handleUploadClick}
              disabled={uploading}
            >
              <Upload size={16} />

              {uploading
                ? "Uploading..."
                : "Upload docs"}
            </button>
          </>
        )}
      </div>

      <div className="docs-shell">
        <div className="docs-tree">
          <div className="tree-head">
            <span>PROJECT DOCUMENTS</span>
          </div>

          {loading ? (
            <div
              style={{
                padding: "16px",
                opacity: 0.65,
              }}
            >
              Loading documents...
            </div>
          ) : documents.length === 0 ? (
            <div
              style={{
                padding: "16px",
                opacity: 0.65,
              }}
            >
              No project documents uploaded yet.
            </div>
          ) : (
            documents.map((document, index) => {
              const filename =
                document.source_file
                  .split("/")
                  .pop() ??
                document.source_file;

              return (
                <button
                  className={
                    selected?.source_file ===
                    document.source_file
                      ? "selected"
                      : ""
                  }
                  onClick={() =>
                    setSelected(document)
                  }
                  key={
                    document.source_file
                  }
                >
                  <FileText size={15} />
                  <span>{filename}</span>

                  {index === 0 && (
                    <span className="new-dot" />
                  )}
                </button>
              );
            })
          )}
        </div>

        <div className="doc-reader">
          <div className="reader-top">
            <div>
              <span className="eyebrow">
                {selected
                  ? `${selectedExtension} · ${updatedLabel}`
                  : "DOCUMENTATION"}
              </span>

              <h2>
                {selectedFilename}
              </h2>
            </div>

            <button className="icon-btn">
              <MoreHorizontal size={18} />
            </button>
          </div>

          <div className="reader-body">
            {selected ? (
              <>
                <p className="reader-kicker">
                  {selected.scope.toUpperCase()} /{" "}
                  {selectedFilename.toUpperCase()}
                </p>

                {documentLines.map(
                  (line, index) => {
                    /*
                     * Preserve the existing reader feel
                     * while displaying the actual document
                     * content returned by the Knowledge Engine.
                     *
                     * Markdown headings become visual headings;
                     * normal lines remain paragraphs.
                     */
                    if (
                      line.startsWith("# ")
                    ) {
                      return (
                        <h3
                          key={`${index}-${line}`}
                        >
                          {line.slice(2)}
                        </h3>
                      );
                    }

                    if (
                      line.startsWith("## ")
                    ) {
                      return (
                        <h4
                          key={`${index}-${line}`}
                        >
                          {line.slice(3)}
                        </h4>
                      );
                    }

                    if (
                      line.startsWith("- ") ||
                      line.startsWith("* ")
                    ) {
                      return (
                        <ul
                          key={`${index}-${line}`}
                        >
                          <li>
                            {line.slice(2)}
                          </li>
                        </ul>
                      );
                    }

                    return (
                      <p
                        key={`${index}-${line}`}
                      >
                        {line}
                      </p>
                    );
                  },
                )}
              </>
            ) : (
              <>
                <p className="reader-kicker">
                  PROJECT DOCUMENTATION
                </p>

                <h3>
                  No document selected.
                </h3>

                <p>
                  Upload a project document to add
                  real engineering context to the
                  Knowledge Engine.
                </p>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

function NotesFeed({
  adminNotes = [],
  gapNotifications = [],
  onViewAnswer,
}: {
  adminNotes?: Array<{
    initials: string;
    color: string;
    name: string;
    role: string;
    time: string;
    text: string;
  }>;
  gapNotifications?: GapNotification[];
  onViewAnswer: (
    notification: GapNotification,
  ) => void;
}) {
  const [showOnline, setShowOnline] =
    useState(false);

  const [noteText, setNoteText] = useState("");

  const notes = [
    {
      initials: "TS",
      color: "#f3b56b",
      name: "Taylor Swift",
      role: "Team admin",
      time: "09:42",
      text: "The API glossary is ready for review. I added the auth edge cases Bob was missing.",
    },
    {
      initials: "MC",
      color: "#8cf7d0",
      name: "Maya Chen",
      role: "Frontend engineer",
      time: "10:06",
      text: "Perfect — I’m moving through Local Setup now. The checkpoint is clear.",
    },
    {
      initials: "AS",
      color: "#9eaaff",
      name: "Aarav Shah",
      role: "Backend engineer",
      time: "10:31",
      text: "Architecture module unlocked on my side. The request flow diagram helped a lot.",
    },
    ...adminNotes,
  ];

  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            TEAM COMMUNICATION / LIVE
          </p>

          <h1>Notes Feed</h1>

          <p>
            Questions, updates, and small signals from
            the people building Atlas Core.
          </p>
        </div>

        <button
          className={`subtle-btn online-toggle ${
            showOnline ? "active" : ""
          }`}
          onClick={() =>
            setShowOnline((current) => !current)
          }
        >
          <Users size={16} /> 4 members online{" "}
          <ChevronDown size={14} />
        </button>
      </div>

      {showOnline && (
        <div className="online-members-panel">
          <div>
            <span className="eyebrow">
              LIVE TEAM PULSE
            </span>

            <h3>Who is online now</h3>
          </div>

          <div className="online-member-list">
            {members.map((member) => (
              <div key={member.name}>
                <Avatar
                  initials={member.initials}
                  color={member.color}
                />

                <span>
                  <strong>{member.name}</strong>
                  <small>{member.role}</small>
                </span>

                <i />
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="notes-shell">
        <div className="notes-stream">
          <div className="stream-day">
            TODAY · THURSDAY
          </div>

          {notes.map((note, index) => (
            <div
              className={`feed-note ${
                note.role === "Team admin"
                  ? "admin-note"
                  : ""
              }`}
              key={`${note.time}-${index}`}
            >
              <Avatar
                initials={note.initials}
                color={note.color}
              />

              <div>
                <div className="feed-meta">
                  <strong>{note.name}</strong>
                  <time>{note.time}</time>
                </div>

                <small className="feed-role">
                  {note.role}
                </small>

                <p>{note.text}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="composer-panel">
          <span className="eyebrow">NEW NOTE</span>

          <textarea
            value={noteText}
            onChange={(event) =>
              setNoteText(event.target.value)
            }
            placeholder="Share an update with the team..."
          />

          <div>
            <span>⌘ ↵ to send</span>

            <button
              className="primary-cta"
              onClick={() => {
                if (noteText.trim()) {
                  setNoteText("");
                }

                toast.success(
                  "Note ready to send once the API is connected.",
                );
              }}
            >
              Post note <ArrowUpRight size={15} />
            </button>
          </div>

          <div className="gap-notification-chat">
            <div className="gap-notification-chat-head">
              <MessageSquare size={16} />
              <h3>Knowledge Gap Updates</h3>
            </div>

            {gapNotifications.length === 0 ? (
              <p className="gap-notification-empty">
                Reviewed gap notifications will appear
                here for the developer who asked the
                question.
              </p>
            ) : (
              gapNotifications.map(
                (notification) => (
                  <article
                    className="gap-notification"
                    key={notification.id}
                  >
                    <div>
                      <strong>
                        {notification.text}
                      </strong>

                      <p>
                        Q: {notification.question}
                      </p>
                    </div>

                    <button
                      className="text-btn"
                      onClick={() =>
                        onViewAnswer(notification)
                      }
                    >
                      View answer{" "}
                      <ArrowUpRight size={13} />
                    </button>
                  </article>
                ),
              )
            )}
          </div>
        </div>
      </div>
    </>
  );
}

function Repository({
  projectId,
  onConnected,
}: {
  projectId: string;
  onConnected: (learningPath: LearningPathResponse) => void;
}) {
  const [repoUrl, setRepoUrl] = useState(
    "https://github.com/ctrlaltelite/atlas-core",
  );
  const [connecting, setConnecting] = useState(false);

  const handleConnect = async () => {
    const url = repoUrl.trim();

    if (!url) {
      toast.error("Please enter a GitHub repository URL.");
      return;
    }

    setConnecting(true);

    try {
      const result = await uploadRepository(url);

      onConnected(result.learning_path);

      toast.success(
        `Repository connected: ${result.project_id}`,
      );

      console.log(
        ">>> REPOSITORY CONNECTED:",
        result,
      );
    } catch (error) {
      toast.error(
        error instanceof Error
          ? error.message
          : "Unable to connect repository.",
      );
    } finally {
      setConnecting(false);
    }
  };

  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            ADMIN / KNOWLEDGE ENGINE INPUT
          </p>

          <h1>Repository</h1>

          <p>
            Connect the codebase that powers your team’s
            onboarding path.
          </p>
        </div>
      </div>

      <div className="repo-shell">
        <div className="repo-connect">
          <div className="dropzone">
            <div className="drop-icon">
              <Github size={22} />
            </div>

            <h3>Connect a GitHub repository</h3>

            <p>
              Paste a repository URL and Devora will map
              the code, docs, and service boundaries.
            </p>

            <div className="repo-input">
              <Github size={16} />

              <input
                value={repoUrl}
                onChange={(event) =>
                  setRepoUrl(event.target.value)
                }
                placeholder="https://github.com/owner/repository"
              />

              <button
                onClick={handleConnect}
                disabled={connecting}
              >
                {connecting ? "Connecting..." : "Connect"}
              </button>
            </div>

            <small>
              Private repositories are supported with the
              future API connection.
            </small>
          </div>
        </div>

        <div className="repo-status">
          <span className="eyebrow">
            PARSER STATUS
          </span>

          <div className="status-line">
            <i className="status-live" />
            <strong>
              Knowledge graph connected
            </strong>
          </div>

          <p>
            Last indexed today at 09:18. 248 files
            understood across 8 service boundaries.
          </p>

          <div className="bar">
            <span style={{ width: "88%" }} />
          </div>

          <div className="repo-stats">
            <span>
              <strong>248</strong> files
            </span>

            <span>
              <strong>8</strong> services
            </span>

            <span>
              <strong>17</strong> docs
            </span>
          </div>
        </div>
      </div>
    </>
  );
}

function MemberStatus({
  focus,
  setFocus,
  memberProgress = {},
}: {
  focus: Member;
  setFocus: (member: Member) => void;
  memberProgress?: Record<string, number>;
}) {
  const visibleMembers = members.map(
    (member) => ({
      ...member,
      progress:
        memberProgress[member.name] ??
        member.progress,
    }),
  );

  const focusProgress =
    memberProgress[focus.name] ??
    focus.progress;

  const focusMember = {
    ...focus,
    progress: focusProgress,
  };

  const moduleRows = [
    {
      name: "Project Overview",
      completion: 100,
      time: "18 min",
      last: "Mon 09:12",
    },
    {
      name: "Local Setup",
      completion:
        focusProgress > 55 ? 100 : 68,
      time: "24 min",
      last: "Today 10:06",
    },
    {
      name: "Architecture",
      completion:
        focusProgress > 65 ? 100 : 18,
      time: "16 min",
      last: "Yesterday 16:40",
    },
    {
      name: "APIs & Data Flow",
      completion:
        focusProgress >= 88
          ? 100
          : focusProgress > 75
            ? 44
            : 0,
      time: "20 min",
      last:
        focusProgress >= 88
          ? "Today · 11:18"
          : "Not started",
    },
    {
      name: "Authentication & Data",
      completion:
        focusProgress >= 100 ? 100 : 0,
      time: "22 min",
      last:
        focusProgress >= 100
          ? "Today · 11:42"
          : "Not started",
    },
  ];

  const status =
    focusProgress >= 100
      ? {
          label: "Complete",
          color: "#8cf7d0",
        }
      : focusProgress >= 60
        ? {
            label: "On track",
            color: "#8cf7d0",
          }
        : focusProgress >= 35
          ? {
              label: "At risk",
              color: "#f3b56b",
            }
          : {
              label: "Needs attention",
              color: "#ff7c8c",
            };

  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            ADMIN / TEAM HEALTH
          </p>

          <h1>Member status</h1>

          <p>
            See where each developer is in their
            onboarding journey.
          </p>
        </div>
      </div>

      <div className="members-layout members-stack">
        <div className="member-table creative-member-list">
          {visibleMembers.map((member) => (
            <button
              key={member.name}
              className={`${
                focus.name === member.name
                  ? "selected"
                  : ""
              } ${
                member.progress < 35
                  ? "needs-attention"
                  : ""
              }`}
              onClick={() => setFocus(member)}
            >
              <Avatar
                initials={member.initials}
                color={member.color}
              />

              <span>
                <strong>{member.name}</strong>
                <small>{member.role}</small>
              </span>

              <div className="member-progress">
                <span>
                  <i
                    style={{
                      width: `${member.progress}%`,
                      background: member.color,
                    }}
                  />
                </span>

                <b>{member.progress}%</b>
              </div>

              <ChevronRight size={16} />
            </button>
          ))}
        </div>

        <div className="member-detail rich-member-detail">
          <div className="member-detail-head">
            <Avatar
              initials={focusMember.initials}
              color={focusMember.color}
            />

            <div>
              <h2>{focusMember.name}</h2>
              <p>
                {focusMember.role} · joined 6 days ago
              </p>
            </div>

            <span
              className="member-health"
              style={{
                color: status.color,
                borderColor: `${status.color}80`,
                background: `${status.color}12`,
              }}
            >
              <i
                style={{
                  background: status.color,
                }}
              />
              {status.label}
            </span>
          </div>

          <div className="member-identity-grid">
            <span>
              <small>TEAM ID</small>
              <strong>atlas-core</strong>
            </span>

            <span>
              <small>ROLE</small>
              <strong>{focusMember.role}</strong>
            </span>

            <span>
              <small>LAST ACTIVE</small>
              <strong>
                {focusMember.name ===
                "Maya Chen"
                  ? focusProgress >= 100
                    ? "Today · 11:42"
                    : "Today · 10:06"
                  : "Yesterday · 16:40"}
              </strong>
            </span>
          </div>

          <section className="member-section">
            <div className="section-head">
              <div>
                <span className="eyebrow">
                  ONBOARDING PROGRESS
                </span>

                <h3>Module by module</h3>
              </div>

              <strong className="member-percent">
                {focusProgress}%
              </strong>
            </div>

            <div className="member-module-list">
              {moduleRows.map((row) => (
                <div key={row.name}>
                  <span>
                    <strong>{row.name}</strong>
                    <small>
                      {row.time} · last accessed{" "}
                      {row.last}
                    </small>
                  </span>

                  <b>{row.completion}%</b>

                  <i>
                    <em
                      style={{
                        width: `${row.completion}%`,
                        background:
                          focusMember.color,
                      }}
                    />
                  </i>
                </div>
              ))}
            </div>
          </section>

          <section className="member-section assistant-activity">
            <div className="section-head">
              <div>
                <span className="eyebrow">
                  AI ASSISTANT ACTIVITY
                </span>

                <h3>
                  Questions that shape the Twin
                </h3>
              </div>

              <BrainCircuit size={17} />
            </div>

            <div className="activity-stat-grid">
              <span>
                <strong>24</strong>
                <small>questions asked</small>
              </span>

              <span>
                <strong>7</strong>
                <small>hints used</small>
              </span>

              <span>
                <strong>Authentication</strong>
                <small>most frequent topic</small>
              </span>
            </div>

            <p>
              <Sparkles size={14} /> Potential knowledge
              gap:{" "}
              <b>
                {focusProgress >= 100
                  ? "None — onboarding complete"
                  : "Authentication and Authorization"}
              </b>
            </p>
          </section>

          <section className="member-section engagement-section">
            <div className="section-head">
              <div>
                <span className="eyebrow">
                  ACTIVITY & ENGAGEMENT
                </span>

                <h3>This week’s rhythm</h3>

                <small className="engagement-note">
                  Calculated from completed modules,
                  tasks, and active learning days.
                </small>
              </div>

              <Zap size={17} />
            </div>

            <div className="engagement-bars">
              {[
                ["Mon", 22],
                ["Tue", 38],
                ["Wed", 18],
                ["Thu", 68],
                ["Fri", 84],
                ["Sat", 28],
                ["Sun", 42],
              ].map(([day, value]) => (
                <span key={day}>
                  <i
                    style={{
                      height: `${value}%`,
                    }}
                  />

                  <small>{day}</small>
                </span>
              ))}
            </div>

            <div className="engagement-meta">
              <span>
                <strong>
                  {focusProgress >= 100 ? "5" : "3"}
                </strong>{" "}
                modules completed
              </span>

              <span>
                <strong>5</strong> day learning streak
              </span>

              <span>
                <strong>
                  {focusProgress >= 100 ? "12" : "8"}
                </strong>{" "}
                tasks completed
              </span>
            </div>
          </section>

          <div className="admin-summary">
            <span className="eyebrow">
              DEVORA SUMMARY
            </span>

            <p>
              {focusProgress >= 100
                ? `${focusMember.name} completed the full onboarding journey and reached 100%.`
                : `${focusMember.name} is progressing ${
                    focusProgress >= 60
                      ? "well overall"
                      : "steadily"
                  } but shows a knowledge gap in authentication and database architecture. Recommend completing the Authentication module before proceeding to Deployment.`}
            </p>
          </div>
        </div>
      </div>
    </>
  );
}

function KnowledgeGapReview({
  inline = false,
  onBack,
  onGapNote,
  projectId = "fastapi-101",
}: {
  inline?: boolean;
  onBack: () => void;
  onGapNote?: (
    notification: GapNotification,
  ) => void;
  projectId?: string;
}) {
  type KnowledgeGap = {
    gap_id: string;
    query: string;
    example_queries: string[];
    project_id: string;
    top_score: number;
    asked_by_developer_id?: string | null;
    developer_ids?: string[];
    status: string;
    occurrence_count: number;
    first_seen_at: string;
    last_seen_at: string;
  };

  const [gaps, setGaps] = useState<KnowledgeGap[]>([]);
  const [uploads, setUploads] = useState<
    Record<string, string>
  >({});
  const [leaving, setLeaving] = useState<string | null>(
    null,
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const loadGaps = async () => {
      try {
        const result = await getKnowledgeGaps(projectId, 2);

        if (!cancelled) {
          setGaps(
            result.gaps.filter(
              (gap) => gap.status === "open",
            ),
          );
        }
      } catch {
        if (!cancelled) {
          toast.error(
            "Could not load knowledge gaps.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    void loadGaps();

    return () => {
      cancelled = true;
    };
  }, [projectId]);

  const openCount = gaps.length;

  const developerName = (
    developerId?: string | null,
  ) => {
    switch (developerId) {
      case "dev-001":
        return "Maya Chen";
      case "dev-002":
        return "Aarav Sharma";
      case "dev-003":
        return "Sofia Rossi";
      case "dev-004":
        return "Noah Williams";
      default:
        return "Developer";
    }
  };

  const markReviewed = async (
    gap: KnowledgeGap,
  ) => {
    const upload = uploads[gap.gap_id];

    if (!upload) {
      toast(
        "Upload a document before marking this gap reviewed.",
      );
      return;
    }

    setLeaving(gap.gap_id);

    try {
      const result = await resolveKnowledgeGap(
        gap.gap_id,
      );

      if (!result.resolved) {
        throw new Error(
          "Knowledge gap could not be resolved.",
        );
      }
      const developerIds = gap.developer_ids?.length
  ? gap.developer_ids
  : gap.asked_by_developer_id
    ? [gap.asked_by_developer_id]
    : [];

for (const developerId of developerIds) {
  await createNotification({
    recipientId: developerId,
    role: "developer",
    text: "Knowledge gap fixed.",
    question: gap.query,
    gapId: gap.gap_id,
  });
}

      const notification: GapNotification = {
        id: `${gap.gap_id}-${Date.now()}`,
        developer: developerName(
          gap.asked_by_developer_id,
        ),
        question: gap.query,
        uploadedContext: upload,
        text: "Knowledge gap fixed.",
      };

      window.setTimeout(() => {
        setGaps((current) =>
          current.filter(
            (item) =>
              item.gap_id !== gap.gap_id,
          ),
        );

        setLeaving(null);
        onGapNote?.(notification);

        toast.success(
          "Knowledge gap resolved. Developer notified in Notes Feed.",
        );
      }, 240);
    } catch {
      setLeaving(null);

      toast.error(
        "Could not resolve this knowledge gap.",
      );
    }
  };

  return (
    <div
      className={`gap-review-page ${
        inline ? "gap-review-inline" : ""
      }`}
    >
      {!inline && (
        <div className="page-heading">
          <div>
            <p className="eyebrow amber-text">
              ADMIN / KNOWLEDGE GAPS
            </p>

            <h1>Review Gaps</h1>

            <p>
              See the questions Bob could not answer
              confidently, then add the context that
              closes the loop.
            </p>
          </div>

          <button
            className="text-btn"
            onClick={onBack}
          >
            Dashboard <ArrowUpRight size={14} />
          </button>
        </div>
      )}

      <div className="gap-review-layout">
        <section className="gap-review-list">
          <div className="gap-review-head">
            <div>
              <span className="eyebrow">
                KNOWLEDGE GAP REVIEW
              </span>

              <h2>
                Questions that need better context.
              </h2>
            </div>

            <span className="gap-count">
              {String(openCount).padStart(2, "0")} open
            </span>
          </div>

          {loading ? (
            <p className="gap-notification-empty">
              Loading knowledge gaps…
            </p>
          ) : gaps.length === 0 ? (
            <p className="gap-notification-empty">
              No open knowledge gaps.
            </p>
          ) : (
            gaps.map((item) => {
              const developer =
                developerName(
                  item.asked_by_developer_id,
                );

              return (
                <article
                  className={`gap-question ${
                    leaving === item.gap_id
                      ? "is-leaving"
                      : ""
                  }`}
                  key={item.gap_id}
                >
                  <div className="gap-question-meta">
                    <Avatar
                      initials={developer
                        .split(" ")
                        .map(
                          (part) => part[0],
                        )
                        .join("")}
                      color="#f3b56b"
                    />

                    <span>
                      <strong>
                        {developer}
                      </strong>

                      <small>
                        Open knowledge gap ·{" "}
                        {item.occurrence_count} occurrence
                        {item.occurrence_count === 1
                          ? ""
                          : "s"}
                      </small>
                    </span>
                  </div>

                  <div className="gap-question-copy">
                    <span className="eyebrow">
                      DEVELOPER QUESTION
                    </span>

                    <p>
                      “{item.query}”
                    </p>

                    <div className="bob-response">
                      <span className="eyebrow">
                        BOB’S RESPONSE
                      </span>

                      <p>
                        Bob could not answer this
                        confidently from the available
                        project context.
                      </p>

                      <small>
                        Knowledge confidence score:{" "}
                        {Math.round(
                          item.top_score * 100,
                        )}
                        %
                      </small>
                    </div>

                    <div className="gap-review-actions">
                      <label
                        className={`gap-upload-drop ${
                          uploads[item.gap_id]
                            ? "uploaded"
                            : ""
                        }`}
                      >
                        <input
                          type="file"
                          accept=".pdf,.doc,.docx,.md,.txt"
                          onChange={(event) => {
                            const file =
                              event.target.files?.[0];

                            if (file) {
                              setUploads(
                                (current) => ({
                                  ...current,
                                  [item.gap_id]:
                                    file.name,
                                }),
                              );
                            }
                          }}
                        />

                        <Upload size={14} />

                        <strong>
                          {uploads[item.gap_id] ??
                            "Upload document"}
                        </strong>

                        <small>
                          {uploads[item.gap_id]
                            ? "Ready to close this gap"
                            : "PDF, DOCX, Markdown, or TXT"}
                        </small>
                      </label>

                      <button
                        className="reviewed-btn"
                        onClick={() =>
                          void markReviewed(item)
                        }
                        disabled={
                          leaving === item.gap_id
                        }
                      >
                        <Check size={14} />
                        Mark reviewed
                      </button>
                    </div>
                  </div>
                </article>
              );
            })
          )}
        </section>

        {!inline && (
          <aside className="gap-upload-card">
            <div className="gap-upload-orb">
              <Upload size={20} />
            </div>

            <span className="eyebrow">
              CLOSE THE GAP
            </span>

            <h2>Add context for Bob.</h2>

            <p>
              Each review accepts its own document so
              the admin can close gaps one by one.
            </p>

            <div className="gap-upload-summary">
              <strong>
                {gaps.length === 0
                  ? "All"
                  : `${openCount}`}
              </strong>

              <span>
                {gaps.length === 0
                  ? "gaps reviewed"
                  : "gaps still open"}
              </span>
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}

function itemKey(index: number) {
  return `gap-${index + 1}`;
}

function ProjectModal({
  projectName,
  onClose,
}: {
  projectName: string;
  onClose: () => void;
}) {
  return (
    <div
      className="modal-backdrop"
      onClick={onClose}
    >
      <div
        className="project-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-head">
          <div>
            <span className="eyebrow">
              PROJECT / {projectName.toUpperCase()}
            </span>

            <h2>Project details</h2>
          </div>

          <button
            className="icon-btn"
            onClick={onClose}
          >
            <X size={18} />
          </button>
        </div>

        <p className="modal-intro">
          A shared map of what the team is building, who
          owns it, and how the pieces connect.
        </p>

        <div className="detail-grid">
  <div>
    <span className="eyebrow">ABOUT</span>
    <p>
  FastAPI-101 is the project currently being
  onboarded through DEVORA. DEVORA connects
  the project repository and documentation to
  a project-specific learning path, knowledge
  gaps, assessments, and grounded answers.
    </p>
  </div>

  <div>
    <span className="eyebrow">TECHNOLOGY</span>
    <p>
      Technology and repository details are derived
      from the connected FastAPI-101 project
      repository and documentation.
    </p>
  </div>

  <div>
    <span className="eyebrow">TEAM</span>
    <p>
  CtrlAltElite is the team currently working
  with this project through DEVORA.
</p>
  </div>

  <div>
    <span className="eyebrow">FLOW</span>
    <p>
      Repository and docs are ingested, the system understands the project, knowledge gaps are mapped, and each developer gets a guided route forward.
    </p>
  </div>
</div>
      </div>
    </div>
  );
}