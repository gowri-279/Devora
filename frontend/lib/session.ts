export type Role = "admin" | "developer";

export function saveSession(token: string, role?: string) {
  localStorage.setItem("mentorspace_token", token);
  if (role) localStorage.setItem("mentorspace_role", role.toLowerCase());
}

export function getRole(): Role {
  return (localStorage.getItem("mentorspace_role") || "developer") as Role;
}

export function logout() {
  localStorage.removeItem("mentorspace_token");
  localStorage.removeItem("mentorspace_role");
}
