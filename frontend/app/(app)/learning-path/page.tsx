"use client";
import { useEffect, useState } from "react";
import { endpoints } from "@/lib/api";
import PageHeader from "@/components/PageHeader";
import Loading from "@/components/Loading";
import ErrorBox from "@/components/ErrorBox";

export default function LearningPath() {
  const [data,setData]=useState<any>(null); const [error,setError]=useState(""); const [loading,setLoading]=useState(false);
  useEffect(()=>{ endpoints.learningPath().then(setData).catch(e=>setError(e.message)); },[]);
  async function generate(){setLoading(true);setError("");try{setData(await endpoints.generateLearningPath())}catch(e:any){setError(e.message)}finally{setLoading(false)}}
  const modules = Array.isArray(data) ? data : (data?.modules || data?.learning_path || []);
  return <><PageHeader title="Learning Path" description="Structured onboarding generated from your repository and documentation." action={<button className="btn-primary" disabled={loading} onClick={generate}>{loading?"Generating...":"Generate learning path"}</button>}/>
    <ErrorBox message={error}/>
    {!data ? <Loading/> : <div className="space-y-3">{modules.length===0 ? <div className="card p-8 text-center text-sm text-slate-500">No learning modules are available yet. Generate a path after uploading your repository and documents.</div> : modules.map((m:any,i:number)=><div className="card p-5" key={m.id??i}><div className="flex gap-4"><div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet/10 font-bold text-violet">{i+1}</div><div className="flex-1"><div className="flex flex-col justify-between gap-2 sm:flex-row"><h2 className="font-bold">{m.title||m.name||`Module ${i+1}`}</h2><span className="badge bg-slate-100 text-slate-600">{m.status||"Not started"}</span></div><p className="mt-1 text-sm leading-6 text-slate-500">{m.description||m.summary||m.objective||"Learning module generated from project context."}</p></div></div></div>)}</div>}
  </>;
}
