// app/api/auth/me/route.ts
import { NextResponse } from "next/server";
import { cookies } from "next/headers";

const ME_URL = `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/me/`;

async function fetchMe(access: string) {
    const r = await fetch(ME_URL, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${access}`,
            "Content-Type": "application/json",
        },
        cache: "no-store",
    });

    const data = await r.json().catch(() => null);
    return { r, data };
}

export async function GET() {
    // ✅ cookies() RETURNS A PROMISE in your setup
    const cookieStore = await cookies();
    const access = cookieStore.get("access_token")?.value;

    if (!access) {
        return NextResponse.json(
            { detail: "Not authenticated" },
            { status: 401 }
        );
    }

    const { r, data } = await fetchMe(access);

    if (!r.ok) {
        return NextResponse.json(
            { detail: "Session expired" },
            { status: 401 }
        );
    }

    return NextResponse.json(
        { status: true, ...data },
        { status: 200 }
    );
}
