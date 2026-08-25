"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { LearningPathMode, LearningPathResponse, LearningPathStep, RepositorySummary, Tab } from "../lib/types";
import { fetchLearningPath } from "../lib/learningPath";

type Confidence = "HIGH"|"MEDIUM"|"LOW";
type BobResponse = {summary:string;confidence:Confidence;source_type:string;reference:string;answer_preview:string;context?:string};
type BobMessage = {id:string;from:"bob"|"user";text:string;response?:BobResponse};
type BobState = "idle"|"listening"|"thinking"|"responding"|"knowledge-gap"|"success"|"warning";
type State = {
 tab:Tab; setTab:(tab:Tab)=>void;
 project:string; setProject:(p:string)=>void;
 steps:LearningPathStep[]; stepsLoading:boolean;
 repositorySummary:RepositorySummary|null; mode:LearningPathMode|null;
 completed:number[]; complete:(step:number)=>void;
 selectedStep:number|null; setSelectedStep:(step:number|null)=>void;
 bobOpen:boolean; setBobOpen:(v:boolean)=>void;
 bobState:BobState; setBobState:(v:BobState)=>void;
 bobMessages:BobMessage[]; addBob:(m:Omit<BobMessage,"id">)=>void;
};
const Ctx=createContext<State|null>(null);
const initialMessages:BobMessage[]=[{id:"bob-boot",from:"bob",text:"Knowledge Engine online. I can help with the active module, repository structure, documentation and your next onboarding checkpoint."}];
const PROGRESS_KEY="devora_progress_v3";
function initialCompleted():Record<string,number[]>{
 if(typeof window==="undefined")return {"payment-service":[1]};
 try{
  const raw=localStorage.getItem(PROGRESS_KEY);
  if(raw)return JSON.parse(raw);
 }catch{}
 return {"payment-service":[1]};
}
export function DevoraProvider({children}:{children:React.ReactNode}){
 const [tab,setTab]=useState<Tab>("command");
 const [project,setProjectState]=useState("payment-service");
 const [completedByProject,setCompletedByProject]=useState<Record<string,number[]>>(initialCompleted);
 const [selectedStep,setSelectedStep]=useState<number|null>(null);
 const [bobOpen,setBobOpen]=useState(false);
 const [bobState,setBobState]=useState<BobState>("idle");
 const [bobMessages,setBobMessages]=useState<BobMessage[]>(initialMessages);
 const [pathData,setPathData]=useState<LearningPathResponse|null>(null);
 const [stepsLoading,setStepsLoading]=useState(true);

 // The learning path is fully backend-driven: whatever the Knowledge Engine's
 // /learning-path endpoint returns for the active project is what renders here.
 useEffect(()=>{
  let cancelled=false;
  setStepsLoading(true);
  fetchLearningPath(project).then(data=>{if(!cancelled){setPathData(data);setStepsLoading(false)}});
  return ()=>{cancelled=true};
 },[project]);

 const steps=pathData?.learning_path||[];
 const repositorySummary=pathData?.repository_summary||null;
 const mode=pathData?.mode||null;
 const completed=completedByProject[project]||[];
 const complete=(step:number)=>setCompletedByProject(v=>{
  const current=v[project]||[];
  if(current.includes(step))return v;
  const next={...v,[project]:[...current,step]};
  if(typeof window!=="undefined")localStorage.setItem(PROGRESS_KEY,JSON.stringify(next));
  return next;
 });
 const setProject=(p:string)=>{setProjectState(p);setSelectedStep(null)};
 const addBob=(m:Omit<BobMessage,"id">)=>setBobMessages(v=>[...v,{...m,id:`bob-${Date.now()}-${v.length}`}]);
 const value=useMemo(()=>({tab,setTab,project,setProject,steps,stepsLoading,repositorySummary,mode,completed,complete,selectedStep,setSelectedStep,bobOpen,setBobOpen,bobState,setBobState,bobMessages,addBob}),[tab,project,steps,stepsLoading,repositorySummary,mode,completed,selectedStep,bobOpen,bobState,bobMessages]);
 return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}
export function useDevora(){const v=useContext(Ctx); if(!v) throw new Error("useDevora must be inside DevoraProvider"); return v;}
export type { BobResponse, BobMessage, BobState };
