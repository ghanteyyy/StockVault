// lib/getCurrentUser.ts
import { backendFetch } from "./backendFetch";

export async function getCurrentUser() {
  // Change this to your real endpoint, e.g. /api/users/me/
  const res = await backendFetch("/api/me/", { method: "GET" });

  if (!res.ok) return null;
  return res.json();
}
