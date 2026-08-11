"use client";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { endpoints } from "@/lib/api";
import { saveSession } from "@/lib/session";
import ErrorBox from "@/components/ErrorBox";

export default function Login() {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault(); setError(""); setLoading(true);
    try {
      const data = await endpoints.login(form);
      const token = data?.access_token || data?.token;
      if (!token) throw new Error("Login succeeded but the backend did not return a JWT token.");
      saveSession(token, data?.role || data?.user?.role);
      router.push("/dashboard");
    } catch (err: any) { setError(err.message); } finally { setLoading(false); }
  }

  return <div className="grid min-h-screen lg:grid-cols-2">
    <div className="hidden bg-navy p-12 text-white lg:flex lg:flex-col lg:justify-between">
      <div><div className="text-xl font-bold">MentorSpace</div><div className="mt-24 max-w-lg"><p className="text-sm font-semibold text-violet-200">AI-POWERED ONBOARDING</p><h1 className="mt-3 text-5xl font-bold leading-tight">Turn your codebase into a learning journey.</h1><p className="mt-5 text-slate-300">Upload your repository and documentation. MentorSpace builds a structured path for every new developer.</p></div></div>
      <p className="text-sm text-slate-400">Repository → Knowledge Engine → Learning Path → Developer</p>
    </div>
    <div className="flex items-center justify-center p-6"><div className="w-full max-w-md">
      <div className="mb-8 lg:hidden"><div className="font-bold text-xl">MentorSpace</div></div>
      <h2 className="text-3xl font-bold">Welcome back</h2><p className="mt-2 text-slate-500">Sign in to continue your onboarding journey.</p>
      <ErrorBox message={error}/>
      <form onSubmit={submit} className="mt-7 space-y-5">
        <div><label className="label">Email</label><input className="input" type="email" required value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></div>
        <div><label className="label">Password</label><input className="input" type="password" required value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/></div>
        <button disabled={loading} className="btn-primary w-full">{loading ? "Signing in..." : "Sign in"}</button>
      </form>
      <p className="mt-6 text-center text-sm text-slate-500">New here? <Link href="/register" className="font-semibold text-violet">Create an account</Link></p>
    </div></div>
  </div>;
}
