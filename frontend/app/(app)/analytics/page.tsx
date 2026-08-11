"use client";
import { useEffect, useState } from "react";
import { endpoints } from "@/lib/api";
import PageHeader from "@/components/PageHeader";
import Loading from "@/components/Loading";
import ErrorBox from "@/components/ErrorBox";

export default function Analytics(){
 const [data,setData]=useState<any>(null); const [error,setError]=useState("");
 useEffect(()=>{endpoints.analytics().then(setData).catch(e=>setError(e.message))},[]);
 if(!data&&!error)return <Loading/>;
 const entries=Object.entries(data||{}).filter(([k,v])=>typeof v==="number"||typeof v==="string");
 return <><PageHeader title="Analytics" description="Progress and onboarding insights returned by GET /analytics."/><ErrorBox message={error}/>
 <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{entries.map(([k,v])=><div className="card p-5" key={k}><p className="text-sm capitalize text-slate-500">{k.replaceAll("_"," ")}</p><p className="mt-2 text-3xl font-bold">{String(v)}</p></div>)}</div>
 <div className="card mt-6 p-6"><h2 className="font-bold">Raw analytics response</h2><pre className="mt-4 max-h-96 overflow-auto rounded-xl bg-slate-950 p-4 text-xs text-slate-200">{JSON.stringify(data,null,2)}</pre></div></>;
}
