import { NextResponse } from "next/server";

export async function POST(req: Request) {
    try {
        const body = await req.json();

        const BASE_URL =process.env.NEXT_PUBLIC_BACKEND_URL || "";

        const r = await fetch(`${BASE_URL}/api/auth/login/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
            cache: "no-store",
        });

        const data = await r.json().catch(() => null);

        if (!r.ok) {
            return NextResponse.json(data ?? { detail: "Login failed" }, { status: r.status });
        }

        const access = data?.tokens?.access ?? data?.access;
        const refresh = data?.tokens?.refresh ?? data?.refresh;

        if (!access || !refresh) {
            return NextResponse.json(
                { detail: "Token response missing access/refresh" },
                { status: 500 }
            );
        }

        const res = NextResponse.json({ access }, { status: 200 });

        const isProd = process.env.NODE_ENV === "production";

        res.cookies.set("access_token", access, {
            httpOnly: true,
            secure: isProd,
            sameSite: "lax",
            path: "/",
            maxAge: 60 * 5,
        });

        res.cookies.set("refresh_token", refresh, {
            httpOnly: true,
            secure: isProd,
            sameSite: "lax",
            path: "/",
            maxAge: 60 * 60 * 24 * 7,
        });

        return res;
    } catch {
        return NextResponse.json({ detail: "Server error" }, { status: 500 });
    }
}
