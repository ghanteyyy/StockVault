// app/api/auth/refresh/route.ts


import { NextResponse } from "next/server";
import { cookies } from "next/headers";

export async function POST() {
    try {
        const cookieStore = await cookies();
        const refresh = cookieStore.get("refresh_token")?.value;

        if (!refresh) {
            return NextResponse.json({ detail: "No refresh token" }, { status: 401 });
        }

        const BASE_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL;
        if (!BASE_URL) {
            return NextResponse.json({ detail: "BACKEND_URL missing" }, { status: 500 });
        }

        const r = await fetch(`${BASE_URL.replace(/\/$/, "")}/api/token/refresh/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh }),
            cache: "no-store",
        });

        const data = await r.json().catch(() => null);

        if (!r.ok) {
            return NextResponse.json(data ?? { detail: "Refresh failed" }, { status: r.status });
        }

        const access: string | undefined = data?.access ?? data?.tokens?.access;
        if (!access) {
            return NextResponse.json(
                { detail: "Access token missing from refresh response" },
                { status: 500 }
            );
        }

        const res = NextResponse.json({ status: true, access }, { status: 200 });

        res.cookies.set("access_token", access, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "lax",
            path: "/",
            maxAge: 60 * 5,
        });

        return res;
    } catch {
        return NextResponse.json({ detail: "Auth server unreachable" }, { status: 503 });
    }
}
