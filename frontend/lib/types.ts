export type Role = "admin" | "developer";
export type Tab = "command" | "repository" | "learning" | "resources" | "notes" | "gaps";
export type User = { id:string; name:string; role:Role; team:string; progress:number; avatar:string; specialty:string; };
export type Session = { user:User; token:string; signedAt:string };
export type RepoModule = { name:string; path:string; files:string[]; tech:string; };

// Shape returned by the Knowledge Engine's repository-aware /learning-path endpoint.
export type LearningPathMode = "repository_aware" | "document_based";
export type LearningPathStep = {
 step:number;
 title:string;
 description:string;
 purpose:string;
 learning_objectives:string[];
 difficulty:string;
 estimated_minutes:number;
 sources:string[];
 evidence:string[];
 confidence:string;
 importance_score:number;
 repository_role:string;
 prerequisites:number[];
 dependents_count:number;
 symbol_count:number;
};
export type RepositorySummary = {
 total_modules_found:number;
 core_modules:number;
 reference_modules:number;
 example_modules:number;
 total_dependencies_analyzed:number;
 entrypoints_found:number;
};
export type LearningPathResponse = {
 project_id:string;
 learning_path:LearningPathStep[];
 repository_summary:RepositorySummary;
 mode:LearningPathMode;
};
