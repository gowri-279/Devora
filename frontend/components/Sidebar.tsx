"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import Icon from "./Icon";
import { getRole, logout } from "@/lib/session";

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const role = typeof window !== "undefined" ? getRole() : "developer";

  const developer = [
    ["/dashboard", "Dashboard", "home"],
    ["/missions", "Missions", "book"],
    ["/learning-path", "Learning Path", "book"],
    ["/bob", "Ask Bob", "bot"],
    ["/notifications", "Notifications", "bell"]
  ];
  const admin = [
    ["/dashboard", "Dashboard", "home"],
    ["/admin/uploads", "Upload", "upload"],
    ["/learning-path", "Learning Path", "book"],
    ["/analytics", "Analytics", "chart"],
    ["/notifications", "Notifications", "bell"]
  ];
  const items = role === "admin" ? admin : developer;

  return (
    <aside className="fixed left-0 top-0 z-30 hidden h-screen w-64 border-r border-slate-200 bg-white px-4 py-5 md:flex md:flex-col">
      <div className="mb-8 flex items-center gap-3 px-2">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet text-white font-bold">M</div>
        <div><div className="font-bold text-slate-900">MentorSpace</div><div className="text-xs text-slate-400">Developer onboarding</div></div>
      </div>
      <nav className="space-y-1">
        {items.map(([href, label, icon]) => (
          <Link key={href} href={href} className={`flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium ${pathname === href ? "bg-violet/10 text-violet" : "text-slate-600 hover:bg-slate-50"}`}>
            <Icon name={icon} />{label}
          </Link>
        ))}
      </nav>
      <div className="mt-auto">
        <div className="mb-3 rounded-2xl bg-slate-50 p-4">
          <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Role</div>
          <div className="mt-1 font-semibold capitalize text-slate-700">{role}</div>
        </div>
        <button className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium text-slate-600 hover:bg-slate-50" onClick={() => { logout(); router.push("/login"); }}>
          <Icon name="logout" />Sign out
        </button>
      </div>
    </aside>
  );
}
