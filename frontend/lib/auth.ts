import { credentials, users } from "./data";
import type { Session } from "./types";

const KEY = "devora_session_v2";
const EVENT = "devora-session-changed";

let snapshot: Session | null = null;
let initialized = false;

function read(): Session | null {
  if (typeof window === "undefined") return null;

  try {
    const raw = window.localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as Session) : null;
  } catch {
    return null;
  }
}

export function getSession(): Session | null {
  if (typeof window === "undefined") return null;

  if (!initialized) {
    snapshot = read();
    initialized = true;
  }

  return snapshot;
}

export function setSession(session: Session | null) {
  if (typeof window === "undefined") return;

  snapshot = session;
  initialized = true;

  if (session) {
    window.localStorage.setItem(KEY, JSON.stringify(session));
  } else {
    window.localStorage.removeItem(KEY);
  }

  window.dispatchEvent(new Event(EVENT));
}

export function subscribeSession(cb: () => void) {
  if (typeof window === "undefined") return () => {};

  const handler = () => {
    snapshot = read();
    initialized = true;
    cb();
  };

  window.addEventListener(EVENT, handler);
  window.addEventListener("storage", handler);

  return () => {
    window.removeEventListener(EVENT, handler);
    window.removeEventListener("storage", handler);
  };
}

export async function login(
  id: string,
  password: string
): Promise<Session> {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL;
  const demo = process.env.NEXT_PUBLIC_DEMO_MODE !== "false";

  console.log("LOGIN CONFIG:", {
    base,
    demo,
  });

  try {
    if (base) {
      const res = await fetch(`${base}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: id,
          password,
        }),
      });

      console.log("LOGIN STATUS:", res.status);

      const data = await res.json();

      console.log("LOGIN RESPONSE:", data);

      if (res.ok) {
        const user = users.find((u) => u.id === id);

        console.log("FRONTEND USER MATCH:", user);

        if (user) {
          return {
            user,
            token:
              data.access_token ??
              data.token ??
              "backend-session",
            signedAt: new Date().toISOString(),
          };
        }

        console.error(
          "LOGIN SUCCESS BUT NO FRONTEND USER MATCH FOR:",
          id
        );
      }
    }
  } catch (err) {
    console.error("BACKEND LOGIN ERROR:", err);
  }

  const match = credentials.find(
    (c) => c.id === id && c.password === password
  );

  if (demo && match) {
    const user = users.find((u) => u.id === id);

    if (user) {
      return {
        user,
        token: `demo-${id}`,
        signedAt: new Date().toISOString(),
      };
    }
  }

  throw new Error(
    "AUTH_FAILURE // credentials rejected or backend unavailable"
  );
}