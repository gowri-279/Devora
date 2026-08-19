"use client";

import { createContext, useContext, useMemo, useState } from "react";
import type { Tab } from "../lib/types";

type Confidence = "HIGH"|"MEDIUM"|"LOW";
type BobResponse = {summary:string;confidence:Confidence;source_type:string;reference:string;answer_preview:string;context?:string};
type BobMessage = {id:string;from:"bob"|"user";text:string;response?:BobResponse};
type BobState = "idle"|"listening"|"thinking"|"responding"|"knowledge-gap"|"success"|"warning";
type State = {
 tab:Tab; setTab:(tab:Tab)=>void;
 completed:string[]; complete:(id:string)=>void;
 project:string; setProject:(p:string)=>void;
 bobOpen:boolean; setBobOpen:(v:boolean)=>void;
 bobState:BobState; setBobState:(v:BobState)=>void;
 bobMessages:BobMessage[]; addBob:(m:Omit<BobMessage,"id">)=>void;
};
const Ctx=createContext<State|null>(null);
const initialMessages:BobMessage[]=[{id:"bob-boot",from:"bob",text:"Knowledge Engine online. I can help with the active module, repository structure, documentation and your next onboarding checkpoint."}];
function initialCompleted(){if(typeof window!=="undefined"){try{return JSON.parse(localStorage.getItem("devora_progress_v1")||"[\"m1\"]") as string[]}catch{return ["m1"]}}return ["m1"]}
export function DevoraProvider({children}:{children:React.ReactNode}){
 const [tab,setTab]=useState<Tab>("command");
 const [completed,setCompleted]=useState<string[]>(initialCompleted);
 const [project,setProject]=useState("payment-service");
 const [bobOpen,setBobOpen]=useState(false);
 const [bobState,setBobState]=useState<BobState>("idle");
 const [bobMessages,setBobMessages]=useState<BobMessage[]>(initialMessages);
 const complete=(id:string)=>setCompleted(v=>{if(v.includes(id))return v; const next=[...v,id]; if(typeof window!=="undefined")localStorage.setItem("devora_progress_v1",JSON.stringify(next)); return next});
 const addBob=(m:Omit<BobMessage,"id">)=>setBobMessages(v=>[...v,{...m,id:`bob-${Date.now()}-${v.length}`}]);
 const value=useMemo(()=>({tab,setTab,completed,complete,project,setProject,bobOpen,setBobOpen,bobState,setBobState,bobMessages,addBob}),[tab,completed,project,bobOpen,bobState,bobMessages]);
 return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}
export function useDevora(){const v=useContext(Ctx); if(!v) throw new Error("useDevora must be inside DevoraProvider"); return v;}
export type { BobResponse, BobMessage, BobState };
