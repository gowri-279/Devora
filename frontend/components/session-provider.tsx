"use client";

import { createContext, useContext, useMemo, useSyncExternalStore } from "react";
import type { Session } from "../lib/types";
import { getSession, setSession, subscribeSession } from "../lib/auth";

type SessionCtx = { session: Session | null; logout: () => void };
const Ctx = createContext<SessionCtx>({ session: null, logout: () => {} });

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const session = useSyncExternalStore(subscribeSession, getSession, () => null);
  const value = useMemo(() => ({ session, logout: () => setSession(null) }), [session]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export const useSession = () => useContext(Ctx);
