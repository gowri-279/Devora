"use client";
import { useEffect, useState } from "react";
import { endpoints } from "@/lib/api";
import PageHeader from "@/components/PageHeader";
import Loading from "@/components/Loading";
import ErrorBox from "@/components/ErrorBox";

export default function Notifications(){
 const [data,setData]=useState<any>(null); const [error,setError]=useState("");
 useEffect(()=>{endpoints.notifications().then(setData).catch(e=>setError(e.message))},[]);
 if(!data&&!error)return <Loading/>;
 const list=Array.isArray(data)?data:(data?.notifications||[]);
 return <><PageHeader title="Notifications" description="Updates from your onboarding workspace."/><ErrorBox message={error}/>
 <div className="space-y-3">{list.length===0?<div className="card p-8 text-center text-sm text-slate-500">No notifications available.</div>:list.map((n:any,i:number)=><div className="card p-5" key={n.id??i}><div className="flex gap-3"><div className="mt-1 h-2.5 w-2.5 rounded-full bg-violet"/><div><h3 className="font-semibold">{n.title||n.type||"Notification"}</h3><p className="mt-1 text-sm text-slate-500">{n.message||n.text||n.description||""}</p>{n.created_at&&<p className="mt-2 text-xs text-slate-400">{n.created_at}</p>}</div></div></div>)}</div></>;
}
