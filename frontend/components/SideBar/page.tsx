"use client";

import React from 'react'
import Link from "next/link";
import Image from "next/image";
import styles from "./sidebar.module.css";
import { useState, useEffect } from "react";
import type { Me } from "@/interface/interfaces";
import { usePathname, useRouter } from 'next/navigation';


const Sidebar = ({ me }: { me: Me }) => {
    const router = useRouter();

    async function logout() {
        await fetch("/api/auth/logout", {
            method: "POST",
            credentials: "include",
        });

        router.replace("/login");
    }

    const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL!;
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const pathname = usePathname();

    const isActive = (path: string) =>
        pathname === path || pathname.startsWith(path + "/");

    return (
        <>
            <aside className={`${styles.sidebar} ${sidebarOpen ? styles.sidebar_open : ''}`}>
                <div className={styles.sidebar_header}>
                    <Image src="/icon.png" alt="Stock Vault" width={40} height={40} />
                    <h2>Stock Vault</h2>
                    <button
                        className={styles.sidebar_close}
                        onClick={() => setSidebarOpen(false)}
                    >
                        <i className="fas fa-times"></i>
                    </button>
                </div>

                <nav className={styles.sidebar_nav}>
                    <Link href="/dashboard" className={isActive("/dashboard") ? styles.nav_item_active : styles.nav_item}>
                        <i className="fas fa-chart-line"></i>
                        <span>Dashboard</span>
                    </Link>

                    <Link href="/portfolio" className={isActive("/portfolio") ? styles.nav_item_active : styles.nav_item}>
                        <i className="fas fa-briefcase"></i>
                        <span>Portfolio</span>
                    </Link>

                    <Link href="/watchlist" className={isActive("/watchlist") ? styles.nav_item_active : styles.nav_item}>
                        <i className="fas fa-star"></i>
                        <span>Watchlist</span>
                    </Link>

                    <Link href="/transactions" className={isActive("/transactions") ? styles.nav_item_active : styles.nav_item}>
                        <i className="fas fa-exchange-alt"></i>
                        <span>Transactions</span>
                    </Link>

                    <Link href="/analytics" className={isActive("/analytics") ? styles.nav_item_active : styles.nav_item}>
                        <i className="fas fa-chart-bar"></i>
                        <span>Analytics</span>
                    </Link>

                    <Link href="/settings" className={isActive("/settings") ? styles.nav_item_active : styles.nav_item}>
                        <i className="fas fa-cog"></i>
                        <span>Settings</span>
                    </Link>
                </nav>

                <div className={styles.sidebar_footer}>
                    <Link href="/profile" className={styles.user_profile}>
                        {me ? (
                            <>
                                <div className={styles.user_avatar}>
                                    <img
                                        className={styles.user_avatar}
                                        src={`${BACKEND_URL.replace(/\/$/, "")}${me.profile_image}`}
                                        alt="Profile"
                                        width={40}
                                        height={40}
                                    />
                                </div>

                                <div className={styles.user_info}>
                                    <p className={styles.user_name}>{me.name}</p>
                                    <p className={styles.user_email}>{me.email}</p>
                                </div>
                            </>
                        ) : (
                            <div className={styles.user_info}>
                                <p className={styles.user_name}>Loading...</p>
                            </div>
                        )}
                    </Link>
                    <button className={styles.logout_button} onClick={logout}>
                        <i className="fas fa-sign-out-alt"></i>
                        <span>Logout</span>
                    </button>
                </div>
            </aside>

            {sidebarOpen && (
                <div
                    className={styles.overlay}
                    onClick={() => setSidebarOpen(false)}
                ></div>
            )}
        </>
    )
}

export default Sidebar;
