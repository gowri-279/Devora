"use client";
import { useEffect, useState } from "react";
import PageHeader from "@/components/PageHeader";
import { endpoints } from "@/lib/api";
import Loading from "@/components/Loading";
import ErrorBox from "@/components/ErrorBox";

export default function Missions() {
  const [items,setItems]=useState<any[]>([]); const [error,setError]=useState("");
  useEffect(()=>{ endpoints.missions().then(d=>setItems(Array.isArray(d)?d:(d?.missions||[]))).catch(e=>setError(e.message)); },[]);
  async function complete(item:any) {
    try {
      const id = item.id ?? item.mission_id ?? item._id;
      await endpoints.completeMission({ mission_id:id, id });
      setItems(items.map(x => (x.id??x.mission_id??x._id)===id ? {...x,completed:true,status:"completed"} : x));
    } catch(e:any){ setError(e.message); }
  }
  return <><PageHeader title="Missions" description="Complete practical tasks generated from your project context."/><ErrorBox message={error}/>
    <div className="space-y-4">{items.length===0 ? <div className="card p-8 text-center text-sm text-slate-500">No missions returned by the backend yet.</div> : items.map((m,i)=><div className="card p-5" key={m.id??m.mission_id??i}>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between"><div><div className="text-xs font-semibold uppercase tracking-wide text-violet">Mission {i+1}</div><h2 className="mt-1 text-lg font-bold">{m.title||m.name||`Mission ${i+1}`}</h2><p className="mt-2 text-sm leading-6 text-slate-500">{m.description||m.summary||"Complete this onboarding mission."}</p></div>
      {(m.completed||m.status==="completed") ? <span className="badge bg-emerald-100 text-emerald-700">Completed</span> : <button onClick={()=>complete(m)} className="btn-primary">Mark complete</button>}</div>
    </div>)}</div>
  </>;
}
