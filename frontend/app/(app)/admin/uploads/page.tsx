"use client";
import { useState } from "react";
import PageHeader from "@/components/PageHeader";
import ErrorBox from "@/components/ErrorBox";
import { endpoints } from "@/lib/api";
import Protected from "@/components/Protected";

export default function Uploads(){
 const [repo,setRepo]=useState<File|null>(null); const [docs,setDocs]=useState<File[]>([]); const [repoStatus,setRepoStatus]=useState(""); const [docStatus,setDocStatus]=useState(""); const [error,setError]=useState("");
 async function uploadRepo(){if(!repo)return;setError("");setRepoStatus("Uploading...");try{const d=await endpoints.uploadRepository(repo);setRepoStatus(d?.message||"Repository uploaded successfully.")}catch(e:any){setError(e.message);setRepoStatus("")}}
 async function uploadDocs(){if(!docs.length)return;setError("");setDocStatus("Uploading...");try{const d=await endpoints.uploadDocuments(docs);setDocStatus(d?.message||"Documents uploaded successfully.")}catch(e:any){setError(e.message);setDocStatus("")}}
 return <Protected role="admin"><PageHeader title="Upload project context" description="Provide the repository and documentation that the parser and Knowledge Engine will use."/><ErrorBox message={error}/>
 <div className="grid gap-6 lg:grid-cols-2">
  <div className="card p-6"><div className="text-xs font-semibold uppercase tracking-wide text-violet">01 · Repository</div><h2 className="mt-2 text-lg font-bold">Upload GitHub repository ZIP</h2><p className="mt-2 text-sm text-slate-500">The backend endpoint is POST /upload/repository. The parser analyzes project structure and returns metadata through the backend.</p><input className="mt-5 block w-full text-sm" type="file" accept=".zip" onChange={e=>setRepo(e.target.files?.[0]||null)}/><button className="btn-primary mt-5" disabled={!repo} onClick={uploadRepo}>Upload repository</button>{repoStatus&&<p className="mt-4 text-sm text-emerald-600">{repoStatus}</p>}</div>
  <div className="card p-6"><div className="text-xs font-semibold uppercase tracking-wide text-violet">02 · Documentation</div><h2 className="mt-2 text-lg font-bold">Upload project documents</h2><p className="mt-2 text-sm text-slate-500">Upload README, architecture docs, API docs, KT notes, PDFs and related files through POST /upload/documents.</p><input className="mt-5 block w-full text-sm" type="file" multiple accept=".pdf,.txt,.md,.doc,.docx" onChange={e=>setDocs(Array.from(e.target.files||[]))}/><div className="mt-3 text-xs text-slate-400">{docs.length} file(s) selected</div><button className="btn-primary mt-5" disabled={!docs.length} onClick={uploadDocs}>Upload documents</button>{docStatus&&<p className="mt-4 text-sm text-emerald-600">{docStatus}</p>}</div>
 </div>
 <div className="card mt-6 p-6"><h2 className="font-bold">Recommended flow</h2><div className="mt-4 grid gap-3 md:grid-cols-4">{["Upload repository","Upload documents","Generate learning path","Review & publish"].map((x,i)=><div key={x} className="rounded-xl bg-slate-50 p-4"><div className="text-xs font-bold text-violet">0{i+1}</div><div className="mt-2 text-sm font-semibold">{x}</div></div>)}</div></div>
 </Protected>;
}
