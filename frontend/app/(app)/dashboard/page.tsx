"use client";
import { useEffect, useState } from "react";
import PageHeader from "@/components/PageHeader";
import { endpoints } from "@/lib/api";
import Loading from "@/components/Loading";
import ErrorBox from "@/components/ErrorBox";

function pick(obj:any, keys:string[], fallback:any=0) { for (const k of keys) if (obj?.[k] !== undefined) return obj[k]; return fallback; }

export default function Dashboard() {
  const [data,setData]=useState<any>(null); const [error,setError]=useState("");
  useEffect(()=>{ endpoints.dashboard().then(setData).catch(e=>setError(e.message)); },[]);
  if (!data && !error) return <Loading/>;
  const stats = [
    ["Modules", pick(data,["total_modules","modules"],0)],
    ["Completed", pick(data,["completed_modules","completed","completed_missions"],0)],
    ["Progress", `${pick(data,["progress","progress_percentage"],0)}%`],
    ["Pending", pick(data,["pending","pending_modules"],0)]
  ];
  return <><PageHeader title="Dashboard" description="Your MentorSpace onboarding workspace."/>
    <ErrorBox message={error}/>
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{stats.map(([label,value])=><div key={label} className="card p-5"><p className="text-sm text-slate-500">{label}</p><p className="mt-2 text-3xl font-bold">{String(value)}</p></div>)}</div>
    <div className="mt-6 grid gap-6 lg:grid-cols-3">
      <div className="card p-6 lg:col-span-2"><h2 className="font-bold">Welcome to your learning workspace</h2><p className="mt-2 text-sm leading-6 text-slate-500">Follow the generated learning path, complete missions, and ask Bob questions using your repository context.</p>
        <div className="mt-6 grid gap-3 sm:grid-cols-3">{["Explore learning path","Complete missions","Ask Bob"].map((x,i)=><div key={x} className="rounded-xl bg-slate-50 p-4"><div className="text-xs font-semibold text-violet">0{i+1}</div><div className="mt-2 font-semibold">{x}</div></div>)}</div>
      </div>
      <div className="card p-6"><h2 className="font-bold">Backend connected</h2><p className="mt-2 text-sm text-slate-500">All dashboard data is loaded through GET /dashboard.</p><div className="mt-5 rounded-xl bg-emerald-50 p-4 text-sm font-medium text-emerald-700">API ready</div></div>
    </div>
  </>;
}
