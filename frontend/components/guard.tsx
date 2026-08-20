"use client";
import { useSession } from "./session-provider";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
export function Guard({children}:{children:React.ReactNode}){const {session}=useSession();const router=useRouter();useEffect(()=>{if(session===null){router.replace("/")}},[session,router]);if(!session)return <div className="cyber-bg grid min-h-screen place-items-center"><div className="glass rounded-2xl px-6 py-5 font-mono text-xs text-cyan-300">[SECURITY] verifying session...</div></div>;return <>{children}</>}
