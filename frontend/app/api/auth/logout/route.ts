// app/api/auth/logout/route.ts

import { NextResponse } from "next/server";
import { cookies } from "next/headers";

export async function POST() {
	const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL!;

	// forward cookies (refresh_token) to backend so it can blacklist it
	const cookieHeader = (await cookies())
		.getAll()
		.map((c) => `${c.name}=${c.value}`)
		.join("; ");

	// Call backend logout
	const r = await fetch(`${BACKEND_URL}/api/auth/logout/`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Cookie: cookieHeader,
		},
		cache: "no-store",
	});

	// Clear cookies on Next.js side (even if backend fails)
	const res = NextResponse.json(
		{ ok: r.ok },
		{ status: r.ok ? 200 : r.status }
	);

	// Clear cookies
	res.cookies.set("refresh_token", "", { path: "/", maxAge: 0 });
	res.cookies.set("access_token", "", { path: "/", maxAge: 0 });

	return res;
}
