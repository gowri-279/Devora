"use client";
import Link from "next/link";
import { useState } from "react";
import Icon from "./Icon";
import { getRole } from "@/lib/session";

export default function MobileHeader() {
  const [open, setOpen] = useState(false);
  const role = typeof window !== "undefined" ? getRole() : "developer";
  const links = role === "admin"
    ? [["/dashboard","Dashboard"],["/admin/uploads","Upload"],["/learning-path","Learning Path"],["/analytics","Analytics"],["/notifications","Notifications"]]
    : [["/dashboard","Dashboard"],["/missions","Missions"],["/learning-path","Learning Path"],["/bob","Ask Bob"],["/notifications","Notifications"]];
  return <div className="sticky top-0 z-20 flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 md:hidden">
    <Link href="/dashboard" className="font-bold">MentorSpace</Link>
    <button onClick={() => setOpen(!open)}><Icon name="menu" /></button>
    {open && <div className="absolute left-0 right-0 top-full border-b bg-white p-3 shadow-lg">
      {links.map(([href,label]) => <Link onClick={() => setOpen(false)} key={href} href={href} className="block rounded-xl px-3 py-3 text-sm">{label}</Link>)}
    </div>}
  </div>;
}
