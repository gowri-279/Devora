export type Role = "admin" | "developer";
export type Tab = "command" | "repository" | "learning" | "resources" | "notes" | "gaps";
export type ModuleStatus = "completed" | "current" | "locked" | "quiz" | "in-progress";
export type User = { id:string; name:string; role:Role; team:string; progress:number; avatar:string; specialty:string; };
export type Session = { user:User; token:string; signedAt:string };
export type Module = { id:string; title:string; description:string; sources:string[]; status:ModuleStatus; duration:string; objectives:string[]; code:string; quiz:{question:string;options:string[];answer:number;hint?:string}[]; };
export type RepoModule = { name:string; path:string; files:string[]; tech:string; };
