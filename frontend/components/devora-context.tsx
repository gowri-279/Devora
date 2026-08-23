"use client";

import { createContext, useContext, useMemo, useState } from "react";
import type { Module, Tab } from "../lib/types";
import { projectModules } from "../lib/data";

type Confidence = "HIGH"|"MEDIUM"|"LOW";
type BobResponse = {summary:string;confidence:Confidence;source_type:string;reference:string;answer_preview:string;context?:string};
type BobMessage = {id:string;from:"bob"|"user";text:string;response?:BobResponse};
type BobState = "idle"|"listening"|"thinking"|"responding"|"knowledge-gap"|"success"|"warning";
type State = {
 tab:Tab; setTab:(tab:Tab)=>void;
 project:string; setProject:(p:string)=>void;
 modules:Module[];
 completed:string[]; complete:(id:string)=>void;
 selectedModuleId:string|null; setSelectedModuleId:(id:string|null)=>void;
 bobOpen:boolean; setBobOpen:(v:boolean)=>void;
 bobState:BobState; setBobState:(v:BobState)=>void;
 bobMessages:BobMessage[]; addBob:(m:Omit<BobMessage,"id">)=>void;
};
const Ctx=createContext<State|null>(null);
const initialMessages:BobMessage[]=[{id:"bob-boot",from:"bob",text:"Knowledge Engine online. I can help with the active module, repository structure, documentation and your next onboarding checkpoint."}];
const PROGRESS_KEY="devora_progress_v2";
function initialCompleted():Record<string,string[]>{
 if(typeof window==="undefined")return {"payment-service":["m1"]};
 try{
  const raw=localStorage.getItem(PROGRESS_KEY);
  if(raw)return JSON.parse(raw);
  const legacy=localStorage.getItem("devora_progress_v1");
  if(legacy)return {"payment-service":JSON.parse(legacy)};
 }catch{}
 return {"payment-service":["m1"]};
}
export function DevoraProvider({children}:{children:React.ReactNode}){
 const [tab,setTab]=useState<Tab>("command");
 const [project,setProjectState]=useState("payment-service");
 const [completedByProject,setCompletedByProject]=useState<Record<string,string[]>>(initialCompleted);
 const [selectedModuleId,setSelectedModuleId]=useState<string|null>(null);
 const [bobOpen,setBobOpen]=useState(false);
 const [bobState,setBobState]=useState<BobState>("idle");
 const [bobMessages,setBobMessages]=useState<BobMessage[]>(initialMessages);
 const modules=projectModules[project as keyof typeof projectModules]||projectModules["payment-service"];
 const completed=completedByProject[project]||[];
 const complete=(id:string)=>setCompletedByProject(v=>{
  const current=v[project]||[];
  if(current.includes(id))return v;
  const next={...v,[project]:[...current,id]};
  if(typeof window!=="undefined")localStorage.setItem(PROGRESS_KEY,JSON.stringify(next));
  return next;
 });
 const setProject=(p:string)=>{setProjectState(p);setSelectedModuleId(null)};
 const addBob=(m:Omit<BobMessage,"id">)=>setBobMessages(v=>[...v,{...m,id:`bob-${Date.now()}-${v.length}`}]);
 const value=useMemo(()=>({tab,setTab,project,setProject,modules,completed,complete,selectedModuleId,setSelectedModuleId,bobOpen,setBobOpen,bobState,setBobState,bobMessages,addBob}),[tab,project,modules,completed,selectedModuleId,bobOpen,bobState,bobMessages]);
 return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}
export function useDevora(){const v=useContext(Ctx); if(!v) throw new Error("useDevora must be inside DevoraProvider"); return v;}
export type { BobResponse, BobMessage, BobState };
