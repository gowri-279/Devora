import { projectModules } from "./data";
import type { LearningPathResponse, LearningPathStep, RepositorySummary } from "./types";

const repositorySummaries: Record<string, RepositorySummary> = {
 "payment-service": { total_modules_found: 203, core_modules: 6, reference_modules: 90, example_modules: 107, total_dependencies_analyzed: 3467, entrypoints_found: 13 },
 "devora": { total_modules_found: 148, core_modules: 5, reference_modules: 62, example_modules: 81, total_dependencies_analyzed: 2210, entrypoints_found: 9 },
 "orders-service": { total_modules_found: 176, core_modules: 5, reference_modules: 74, example_modules: 97, total_dependencies_analyzed: 2890, entrypoints_found: 11 },
};

const difficultyForIndex = (i: number) => (i < 2 ? "easy" : i < 5 ? "medium" : "hard");
const roleForIndex = (i: number, total: number) => (i === 0 ? "foundation" : i === total - 1 ? "integration" : "core");
const minutesFromDuration = (duration: string) => parseInt(duration, 10) || 20;

// Used only when NEXT_PUBLIC_API_BASE_URL is unset or the backend is unreachable,
// so the UI still has something real to render during local development.
function buildFallbackLearningPath(projectId: string): LearningPathResponse {
 const modules = projectModules[projectId as keyof typeof projectModules] || projectModules["payment-service"];
 const learning_path: LearningPathStep[] = modules.map((m, i) => ({
  step: i + 1,
  title: m.title,
  description: m.description,
  purpose: m.description,
  learning_objectives: m.objectives,
  difficulty: difficultyForIndex(i),
  estimated_minutes: minutesFromDuration(m.duration),
  sources: m.sources,
  evidence: m.sources,
  confidence: i < modules.length - 2 ? "high" : "medium",
  importance_score: Math.max(0.3, +(1 - i * 0.12).toFixed(2)),
  repository_role: roleForIndex(i, modules.length),
  prerequisites: i === 0 ? [] : [i],
  dependents_count: Math.max(0, modules.length - i - 1),
  symbol_count: 8 + i * 4,
 }));
 return {
  project_id: projectId,
  learning_path,
  repository_summary: repositorySummaries[projectId] || repositorySummaries["payment-service"],
  mode: "repository_aware",
 };
}

function isLearningPathResponse(v: unknown): v is LearningPathResponse {
 return !!v && typeof v === "object" && Array.isArray((v as any).learning_path);
}

export async function fetchLearningPath(projectId: string): Promise<LearningPathResponse> {
 const base = process.env.NEXT_PUBLIC_API_BASE_URL;
 if (base) {
  try {
   const res = await fetch(`${base}/learning-path?project_id=${encodeURIComponent(projectId)}`);
   if (res.ok) {
    const data = await res.json();
    if (isLearningPathResponse(data)) return data;
   }
  } catch {
   // backend unreachable — fall through to the local fallback below
  }
 }
 return buildFallbackLearningPath(projectId);
}
