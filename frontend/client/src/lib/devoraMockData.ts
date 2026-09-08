// Signal Garden data boundary: keep demo parsing and structured insights replaceable by real profile, Bob, repo, and company-context APIs.

export type SkillProfile = {
  name: string;
  fileName: string;
  source: string;
  skills: Record<string, number>;
};

export type ModulePlan = {
  title: string;
  desc: string;
  time: string;
  status: "complete" | "current" | "locked" | "recommended" | "skipped";
  tag: string;
  reason: string;
};

export type TwinSnapshot = {
  overall: number;
  strengths: { label: string; score: number; color: string }[];
  gaps: { label: string; score: number; delta: string }[];
  evolution: { label: string; before: number; after: number }[];
  signal: string;
};

export type HeatmapRow = {
  name: string;
  initials: string;
  color: string;
  scores: Record<string, number>;
  status: string;
};

export const skillCategories = ["APIs", "Architecture", "Database", "Security"];

export const defaultSkillProfile: SkillProfile = {
  name: "Maya Chen",
  fileName: "maya-skill-profile.pdf",
  source: "Skill profile · uploaded during signup",
  skills: { APIs: 66, Architecture: 48, Database: 38, Security: 44 },
};

export function parseSkillProfile(fileName = "skill-profile.pdf", name = "Maya Chen"): SkillProfile {
  const seed = fileName.toLowerCase();
  const backendLean = seed.includes("backend") || seed.includes("api");
  const frontendLean = seed.includes("frontend") || seed.includes("react");
  const skills = backendLean
    ? { APIs: 74, Architecture: 61, Database: 69, Security: 52 }
    : frontendLean
      ? { APIs: 63, Architecture: 54, Database: 34, Security: 46 }
      : { ...defaultSkillProfile.skills };
  return { name, fileName, source: `Parsed locally · ${fileName}`, skills };
}

export function personalizeModules(profile: SkillProfile): ModulePlan[] {
  const architecture = profile.skills.Architecture;
  const database = profile.skills.Database;
  const security = profile.skills.Security;
  return [
    { title: "Project Overview", desc: "Learn the product vocabulary, team map, and the why behind the repository.", time: "12 min", status: "complete", tag: "01", reason: "Already mapped from your profile." },
    { title: "Local Setup", desc: "Get the project running locally and understand the environment contract.", time: profile.skills.APIs > 70 ? "10 min" : "18 min", status: "current", tag: "02", reason: profile.skills.APIs > 70 ? "Shortened — you already understand the project interfaces." : "A practical first step for your profile." },
    { title: "Architecture", desc: "Trace requests across the client, service layer, and Knowledge Engine.", time: architecture > 60 ? "14 min" : "24 min", status: architecture > 72 ? "skipped" : "recommended", tag: "03", reason: architecture > 72 ? "Skipped — strong architecture signal." : "Recommended to close a context gap." },
    { title: "APIs & Data Flow", desc: "Understand the integration points that power grounded onboarding.", time: profile.skills.APIs > 72 ? "12 min" : "20 min", status: profile.skills.APIs > 78 ? "skipped" : "locked", tag: "04", reason: profile.skills.APIs > 78 ? "Skipped — API fluency already detected." : "Unlocks after Architecture." },
    { title: "Security & Data", desc: "Make authorization, persistence, and service boundaries feel predictable.", time: database < 45 || security < 50 ? "22 min" : "14 min", status: database < 45 || security < 50 ? "recommended" : "locked", tag: "05", reason: database < 45 || security < 50 ? "Prioritized from your skill profile." : "Available when your path expands." },
  ];
}

export function buildTwin(profile: SkillProfile, assessmentComplete = false): TwinSnapshot {
  const values = Object.values(profile.skills);
  const overall = Math.round(values.reduce((sum, value) => sum + value, 0) / values.length + (assessmentComplete ? 8 : 0));
  return {
    overall,
    strengths: [
      { label: "APIs", score: Math.min(98, profile.skills.APIs + (assessmentComplete ? 4 : 0)), color: "#8cf7d0" },
      { label: "Architecture", score: Math.min(96, profile.skills.Architecture + (assessmentComplete ? 5 : 0)), color: "#9eaaff" },
      { label: "Security", score: Math.min(96, profile.skills.Security + (assessmentComplete ? 3 : 0)), color: "#e8a2f7" },
    ],
    gaps: [
      { label: profile.skills.Database < profile.skills.Security ? "Database" : "Security", score: Math.min(profile.skills.Database, profile.skills.Security), delta: "+18% target" },
      { label: "Architecture", score: profile.skills.Architecture, delta: "+12% target" },
      { label: "Team vocabulary", score: 57 + (assessmentComplete ? 13 : 0), delta: assessmentComplete ? "+13% this path" : "Context Signal" },
    ],
    evolution: [
      { label: "Repository context", before: 42, after: Math.min(92, profile.skills.Architecture + (assessmentComplete ? 20 : 12)) },
      { label: "Service boundaries", before: 36, after: Math.min(88, profile.skills.APIs + (assessmentComplete ? 13 : 7)) },
      { label: "Team language", before: 29, after: assessmentComplete ? 81 : 58 },
    ],
    signal: assessmentComplete ? "Your Twin is updated from Bob’s assessment read." : "Your Twin is learning from your profile, repository, and company context.",
  };
}

export const assessmentQuestions = [
  "An API request is returning an unexpected error even though the endpoint exists and the request is being sent correctly. How would you investigate the issue, and what would you check first?",
  "A new feature needs to be added to the application without affecting the existing features. How would you decide where and how to implement it? Explain your reasoning.",
  "A page that retrieves data from the database has suddenly become very slow as the amount of data has increased. What could be causing this, and how would you investigate and improve it?",
  "A developer can access a feature that should only be available to administrators. How would you identify the problem and prevent unauthorized access?",
  "A feature works correctly on your local machine but fails when deployed. Walk through your approach to identifying the cause and fixing the issue.",
];

const assessmentSignals = [
  ["api", "endpoint", "request", "error", "response", "status", "header", "contract", "log"],
  ["feature", "boundary", "ownership", "layer", "component", "service", "dependency", "interface", "impact"],
  ["database", "query", "index", "schema", "migration", "join", "cache", "plan", "timeout"],
  ["admin", "role", "permission", "authorize", "authorization", "session", "token", "access", "validate"],
];

function scoreAnswer(answer: string, signals: string[]) {
  const normalized = answer.trim().toLowerCase();
  const lengthSignal = Math.min(38, Math.floor(normalized.length / 12));
  const keywordSignal = Math.min(32, signals.reduce((hits, signal) => hits + (normalized.includes(signal) ? 4 : 0), 0));
  return Math.min(100, 30 + lengthSignal + keywordSignal);
}

export function analyzeAssessment(answers: Record<number, string>): { summary: string; scores: Record<string, number>; nextFocus: string } {
  const scenario = answers[4] ?? "";
  const categories = skillCategories.map((category, index) => {
    const primary = scoreAnswer(answers[index] ?? "", assessmentSignals[index]);
    const combined = scoreAnswer(scenario, [...assessmentSignals[index], "deploy", "production", "environment", "configuration", "logs", "rollback"]);
    return { category, score: Math.round(primary * 0.75 + combined * 0.25) };
  });
  const scores = Object.fromEntries(categories.map(({ category, score }) => [category, score]));
  const nextFocus = [...categories].sort((a, b) => a.score - b.score)[0].category;
  const average = Math.round(categories.reduce((sum, item) => sum + item.score, 0) / categories.length);
  return {
    summary: average >= 72 ? "Bob found strong application-based reasoning across the four core areas." : "Bob found a practical foundation and identified the lowest-scoring core area for focused practice.",
    scores,
    nextFocus,
  };
}

export const heatmapRows: HeatmapRow[] = [
  { name: "Maya Chen", initials: "MC", color: "#8cf7d0", scores: { APIs: 84, Architecture: 72, Database: 47, Security: 52 }, status: "Assessment analyzed" },
  { name: "Aarav Shah", initials: "AS", color: "#9eaaff", scores: { APIs: 91, Architecture: 88, Database: 82, Security: 68 }, status: "Learning path active" },
  { name: "Sofia Rossi", initials: "SR", color: "#f3b56b", scores: { APIs: 57, Architecture: 61, Database: 44, Security: 39 }, status: "Needs focus" },
  { name: "Noah Williams", initials: "NW", color: "#e8a2f7", scores: { APIs: 36, Architecture: 42, Database: 31, Security: 28 }, status: "Profile imported" },
];

export function heatmapAverages(rows = heatmapRows) {
  return skillCategories.map((category) => ({ category, score: Math.round(rows.reduce((sum, row) => sum + row.scores[category], 0) / rows.length) }));
}
