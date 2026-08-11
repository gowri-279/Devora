export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

type ApiOptions = RequestInit & { auth?: boolean };

export async function api<T = any>(
  path: string,
  options: ApiOptions = {}
): Promise<T> {
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData)) headers.set("Content-Type", "application/json");

  if (options.auth !== false && typeof window !== "undefined") {
    const token = localStorage.getItem("mentorspace_token");
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    cache: "no-store"
  });

  const contentType = res.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await res.json()
    : await res.text();

  if (!res.ok) {
    const message =
      typeof data === "object" && data?.detail
        ? data.detail
        : typeof data === "string" && data
          ? data
          : `Request failed (${res.status})`;
    throw new Error(message);
  }
  return data as T;
}

export const endpoints = {
  register: (body: unknown) => api("/register", { method: "POST", body: JSON.stringify(body), auth: false }),
  login: (body: unknown) => api("/login", { method: "POST", body: JSON.stringify(body), auth: false }),
  dashboard: () => api("/dashboard"),
  missions: () => api("/missions"),
  completeMission: (body: unknown) => api("/complete-mission", { method: "POST", body: JSON.stringify(body) }),
  learningPath: () => api("/learning-path"),
  generateLearningPath: () => api("/generate-learning-path", { method: "POST" }),
  uploadRepository: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api("/upload/repository", { method: "POST", body: form });
  },
  uploadDocuments: (files: File[]) => {
    const form = new FormData();
    files.forEach(file => form.append("files", file));
    return api("/upload/documents", { method: "POST", body: form });
  },
  notifications: () => api("/notifications"),
  analytics: () => api("/analytics"),
  askBob: (body: unknown) => api("/ask-bob", { method: "POST", body: JSON.stringify(body) })
};
