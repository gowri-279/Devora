"use client";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { endpoints } from "@/lib/api";
import { saveSession } from "@/lib/session";
import ErrorBox from "@/components/ErrorBox";

export default function Register() {
  const router = useRouter();
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "developer" });
  const [error, setError] = useState(""); const [loading, setLoading] = useState(false);
  async function submit(e: FormEvent) {
    e.preventDefault(); setError(""); setLoading(true);
    try {
      const data = await endpoints.register(form);
      const token = data?.access_token || data?.token;
      if (token) { saveSession(token, data?.role || form.role); router.push("/dashboard"); }
      else router.push("/login");
    } catch (err: any) { setError(err.message); } finally { setLoading(false); }
  }
  return <div className="flex min-h-screen items-center justify-center p-6"><div className="w-full max-w-md">
    <div className="mb-8"><div className="text-xl font-bold">MentorSpace</div><h1 className="mt-8 text-3xl font-bold">Create your account</h1><p className="mt-2 text-slate-500">Join your team's developer onboarding workspace.</p></div>
    <ErrorBox message={error}/>
    <form onSubmit={submit} className="space-y-4">
      <div><label className="label">Name</label><input className="input" required value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/></div>
      <div><label className="label">Email</label><input className="input" type="email" required value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></div>
      <div><label className="label">Password</label><input className="input" type="password" required value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/></div>
      <div><label className="label">Role</label><select className="input" value={form.role} onChange={e=>setForm({...form,role:e.target.value})}><option value="developer">Developer</option><option value="admin">Admin</option></select></div>
      <button disabled={loading} className="btn-primary w-full">{loading ? "Creating..." : "Create account"}</button>
    </form>
    <p className="mt-6 text-center text-sm text-slate-500">Already registered? <Link href="/login" className="font-semibold text-violet">Sign in</Link></p>
  </div></div>;
}
