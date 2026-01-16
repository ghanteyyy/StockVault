"use client";

import React from 'react'
import Link from "next/link";
import Image from "next/image";
import styles from "./sidebar.module.css";
import { useState, useEffect } from "react";
import type { Me } from "@/interface/interfaces";


const Sidebar = () => {
    const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL!;
    const [me, setMe] = useState<Me | null>(null);

    useEffect(() => {
        (async () => {
            const r = await fetch("/api/auth/me", {
                credentials: "include",
                cache: "no-store",
            });

            if (r.status === 401) {
                window.location.href = "/login";
                return;
            }

            const data = await r.json();
            setMe(data.me);
        })();
    }, []);

    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <>
            {/* Sidebar */}
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
                    <Link href="/dashboard" className={styles.nav_item_active}>
                        <i className="fas fa-chart-line"></i>
                        <span>Dashboard</span>
                    </Link>
                    <Link href="/portfolio" className={styles.nav_item}>
                        <i className="fas fa-briefcase"></i>
                        <span>Portfolio</span>
                    </Link>
                    <Link href="/watchlist" className={styles.nav_item}>
                        <i className="fas fa-star"></i>
                        <span>Watchlist</span>
                    </Link>
                    <Link href="/transactions" className={styles.nav_item}>
                        <i className="fas fa-exchange-alt"></i>
                        <span>Transactions</span>
                    </Link>
                    <Link href="/analytics" className={styles.nav_item}>
                        <i className="fas fa-chart-bar"></i>
                        <span>Analytics</span>
                    </Link>
                    <Link href="/settings" className={styles.nav_item}>
                        <i className="fas fa-cog"></i>
                        <span>Settings</span>
                    </Link>
                </nav>

                <div className={styles.sidebar_footer}>
                    <Link href="/profile" className={styles.user_profile}>
                        <div className={styles.user_avatar}>
                            <img className={styles.user_avatar}
                            src={`${BACKEND_URL.replace(/\/$/, "")}${me?.profile_image ?? ""}`}
                            alt="Profile"
                            width={40}
                            height={40}
                            />
                        </div>
                        <div className={styles.user_info}>
                            <p className={styles.user_name}>{me?.name}</p>
                            <p className={styles.user_email}>{me?.email}</p>
                        </div>
                    </Link>
                    <button className={styles.logout_button}>
                        <i className="fas fa-sign-out-alt"></i>
                        <span>Logout</span>
                    </button>
                </div>
            </aside>

            {/* Overlay */}
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
