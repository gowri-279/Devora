"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getRole } from "@/lib/session";
import Loading from "./Loading";

export default function Protected({ children, role }: { children: React.ReactNode; role?: "admin" | "developer" }) {
  const router = useRouter();
  const [ok, setOk] = useState(false);
  useEffect(() => {
    const token = localStorage.getItem("mentorspace_token");
    const currentRole = getRole();
    if (!token) router.replace("/login");
    else if (role && currentRole !== role) router.replace("/dashboard");
    else setOk(true);
  }, [router, role]);
  if (!ok) return <Loading />;
  return <>{children}</>;
}
