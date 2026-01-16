import "../globals.css";
import SideBar from "@/components/SideBar/page";
import { headers } from "next/headers";
import type { Me } from "@/interface/interfaces";


async function getMe() {
	const r = await fetch("http://localhost:3000/api/auth/me", {
		headers: {
			cookie: (await headers()).get("cookie") ?? "",
		},
		cache: "no-store",
	});

	if (!r.ok) return null;
	return r.json();
}


export default async function Layout({
	children,
}: Readonly<{ children: React.ReactNode }>) {
	const me = await getMe();

	return (
		<html lang="en">
			<head>
				<link
					href="https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css"
					rel="stylesheet"
				/>
				<link
					rel="stylesheet"
					href="https://cdn.jsdelivr.net/gh/iconoir-icons/iconoir@main/css/iconoir.css"
				/>
				<link
					rel="stylesheet"
					href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
				/>

				<link rel="preconnect" href="https://fonts.googleapis.com" />
				<link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
				<link
					href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap"
					rel="stylesheet"
				/>
			</head>
			<body
			>
				<SideBar me={me?.me} />
				{children}
			</body>
		</html>
	);
}
