// lib/backendFetch.ts

import { cookies } from "next/headers";

type FetchOptions = RequestInit & { retry?: boolean };

async function refreshAccessToken(refresh: string) {
    const r = await fetch(`${process.env.BACKEND_URL}/api/token/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh }),
        cache: "no-store",
    });

    const data = await r.json().catch(() => null);
    if (!r.ok) return null;

    return data?.access as string | null;
}

export async function backendFetch(path: string, options: FetchOptions = {}) {
    const cookieStore = cookies();
    const access = (await cookieStore).get("access_token")?.value;
    const refresh = (await cookieStore).get("refresh_token")?.value;

    const headers = new Headers(options.headers);
    headers.set("Content-Type", headers.get("Content-Type") ?? "application/json");
    if (access) headers.set("Authorization", `Bearer ${access}`);

    const doFetch = (authAccess?: string) => {
        const h = new Headers(headers);
        if (authAccess) h.set("Authorization", `Bearer ${authAccess}`);
        return fetch(`${process.env.BACKEND_URL}${path}`, {
            ...options,
            headers: h,
            cache: "no-store",
        });
    };

    const res = await doFetch();

    // If access expired, refresh and retry once
    if (res.status === 401 && options.retry !== false && refresh) {
        const newAccess = await refreshAccessToken(refresh);
        if (!newAccess) return res;

        // Try to update cookie (works in route handlers / server actions; harmless if it can't)
        try {
            (await cookieStore).set("access_token", newAccess, {
                httpOnly: true,
                secure: process.env.NODE_ENV === "production",
                sameSite: "lax",
                path: "/",
                maxAge: 60 * 5,
            });
        } catch { }

        return doFetch(newAccess);
    }

    return res;
}
