"use client";
import { FormEvent, useState } from "react";
import { endpoints } from "@/lib/api";
import PageHeader from "@/components/PageHeader";
import ErrorBox from "@/components/ErrorBox";

export default function Bob() {
  const [question,setQuestion]=useState(""); const [answer,setAnswer]=useState(""); const [error,setError]=useState(""); const [loading,setLoading]=useState(false);
  async function ask(e:FormEvent){e.preventDefault();if(!question.trim())return;setLoading(true);setError("");try{const d=await endpoints.askBob({question});setAnswer(d?.answer||d?.response||d?.message||JSON.stringify(d,null,2))}catch(e:any){setError(e.message)}finally{setLoading(false)}}
  return <><PageHeader title="Ask Bob" description="Ask questions using context retrieved from your repository and documentation."/><ErrorBox message={error}/>
    <div className="grid gap-6 lg:grid-cols-[1fr_360px]"><div className="card p-6"><form onSubmit={ask}><label className="label">Your question</label><textarea className="input min-h-36 resize-y" placeholder="How does authentication work in this project?" value={question} onChange={e=>setQuestion(e.target.value)}/><div className="mt-4 flex justify-end"><button className="btn-primary" disabled={loading}>{loading?"Thinking...":"Ask Bob"}</button></div></form>
      {answer && <div className="mt-6 rounded-2xl bg-slate-50 p-5"><div className="text-xs font-semibold uppercase tracking-wide text-violet">Bob's answer</div><div className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-700">{answer}</div></div>}
    </div><div className="card p-6"><div className="flex h-12 w-12 items-center justify-center rounded-xl bg-violet/10 text-violet">AI</div><h2 className="mt-4 font-bold">Context-aware assistance</h2><p className="mt-2 text-sm leading-6 text-slate-500">The frontend sends your question to the backend. The Knowledge Engine retrieves relevant context, and the backend forwards that context to IBM Bob.</p></div></div>
  </>;
}
