"use client";

import Link from 'next/link';
import { useState, useEffect } from 'react';
import styles from './dashboard.module.css';
import type { Me } from '@/interface/interfaces'


const DashboardPage = () => {
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

    // Mock data - replace with actual API data
    const portfolioData = {
        totalValue: 125450.50,
        todayChange: 2345.20,
        todayChangePercent: 1.91,
        totalGain: 15450.50,
        totalGainPercent: 14.05
    };

    const holdings = [
        { id: 1, symbol: 'NABIL', name: 'Nabil Bank Ltd', shares: 100, avgPrice: 850.00, currentPrice: 920.50, value: 92050, gain: 7050, gainPercent: 8.29 },
        { id: 2, symbol: 'NICA', name: 'NIC Asia Bank', shares: 50, avgPrice: 720.00, currentPrice: 695.00, value: 34750, gain: -1250, gainPercent: -3.47 },
        { id: 3, symbol: 'UPPER', name: 'Upper Tamakoshi', shares: 25, avgPrice: 450.00, currentPrice: 480.00, value: 12000, gain: 750, gainPercent: 6.67 },
    ];

    const watchlist = [
        { symbol: 'ADBL', name: 'Agriculture Development Bank', price: 385.00, change: 5.20, changePercent: 1.37 },
        { symbol: 'HIDCL', name: 'Hydroelectricity Investment', price: 295.50, change: -2.50, changePercent: -0.84 },
        { symbol: 'NLIC', name: 'Nepal Life Insurance', price: 1250.00, change: 15.00, changePercent: 1.22 },
    ];

    const recentActivity = [
        { id: 1, type: 'buy', symbol: 'NABIL', shares: 10, price: 920.50, date: '2026-01-14', time: '10:30 AM' },
        { id: 2, type: 'sell', symbol: 'NICA', shares: 20, price: 695.00, date: '2026-01-13', time: '02:15 PM' },
        { id: 3, type: 'buy', symbol: 'UPPER', shares: 5, price: 480.00, date: '2026-01-12', time: '11:45 AM' },
    ];

    return (
        <div className={styles.dashboard}>
            {/* Main Content */}
            <main className={styles.main_content}>
                {/* Top Bar */}
                <header className={styles.top_bar}>
                    <button
                        className={styles.menu_button}
                        onClick={() => setSidebarOpen(true)}
                    >
                        <i className="fas fa-bars"></i>
                    </button>

                    <h1>Dashboard</h1>
                    <div className={styles.top_bar_actions}>
                        <button className={styles.notification_button}>
                            <i className="fas fa-bell"></i>
                            <span className={styles.notification_badge}>3</span>
                        </button>
                    </div>
                </header>

                {/* Dashboard Content */}
                <div className={styles.dashboard_content}>
                    {/* Portfolio Overview Cards */}
                    <div className={styles.overview_cards}>
                        <div className={styles.overview_card}>
                            <div className={styles.card_header}>
                                <i className="fas fa-wallet"></i>
                                <span>Total Portfolio Value</span>
                            </div>
                            <div className={styles.card_value}>
                                NPR {portfolioData.totalValue.toLocaleString('en-NP', { minimumFractionDigits: 2 })}
                            </div>
                            <div className={`${styles.card_change} ${portfolioData.todayChange >= 0 ? styles.positive : styles.negative}`}>
                                <i className={portfolioData.todayChange >= 0 ? "fas fa-arrow-up" : "fas fa-arrow-down"}></i>
                                NPR {Math.abs(portfolioData.todayChange).toLocaleString('en-NP', { minimumFractionDigits: 2 })} ({portfolioData.todayChangePercent}%) Today
                            </div>
                        </div>

                        <div className={styles.overview_card}>
                            <div className={styles.card_header}>
                                <i className="fas fa-chart-line"></i>
                                <span>Total Gain/Loss</span>
                            </div>
                            <div className={styles.card_value}>
                                NPR {portfolioData.totalGain.toLocaleString('en-NP', { minimumFractionDigits: 2 })}
                            </div>
                            <div className={`${styles.card_change} ${portfolioData.totalGain >= 0 ? styles.positive : styles.negative}`}>
                                <i className={portfolioData.totalGain >= 0 ? "fas fa-arrow-up" : "fas fa-arrow-down"}></i>
                                {portfolioData.totalGainPercent}% Overall
                            </div>
                        </div>

                        <div className={styles.overview_card}>
                            <div className={styles.card_header}>
                                <i className="fas fa-coins"></i>
                                <span>Holdings</span>
                            </div>
                            <div className={styles.card_value}>{holdings.length}</div>
                            <div className={styles.card_subtitle}>Active Stocks</div>
                        </div>

                        <div className={styles.overview_card}>
                            <div className={styles.card_header}>
                                <i className="fas fa-eye"></i>
                                <span>Watchlist</span>
                            </div>
                            <div className={styles.card_value}>{watchlist.length}</div>
                            <div className={styles.card_subtitle}>Stocks Watching</div>
                        </div>
                    </div>

                    {/* Holdings Table */}
                    <div className={styles.section_card}>
                        <div className={styles.section_header}>
                            <h2>Your Holdings</h2>
                            <Link href="/portfolio" className={styles.view_all}>
                                View All <i className="fas fa-arrow-right"></i>
                            </Link>
                        </div>
                        <div className={styles.table_container}>
                            <table className={styles.holdings_table}>
                                <thead>
                                    <tr>
                                        <th>Symbol</th>
                                        <th>Company</th>
                                        <th>Shares</th>
                                        <th>Avg Price</th>
                                        <th>Current Price</th>
                                        <th>Value</th>
                                        <th>Gain/Loss</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {holdings.map(holding => (
                                        <tr key={holding.id}>
                                            <td className={styles.symbol_cell}>
                                                <strong>{holding.symbol}</strong>
                                            </td>
                                            <td>{holding.name}</td>
                                            <td>{holding.shares}</td>
                                            <td>NPR {holding.avgPrice.toFixed(2)}</td>
                                            <td>NPR {holding.currentPrice.toFixed(2)}</td>
                                            <td>NPR {holding.value.toLocaleString('en-NP')}</td>
                                            <td className={holding.gain >= 0 ? styles.positive : styles.negative}>
                                                <div className={styles.gain_cell}>
                                                    <span>NPR {Math.abs(holding.gain).toLocaleString('en-NP')}</span>
                                                    <span className={styles.percent}>
                                                        <i className={holding.gain >= 0 ? "fas fa-caret-up" : "fas fa-caret-down"}></i>
                                                        {Math.abs(holding.gainPercent)}%
                                                    </span>
                                                </div>
                                            </td>
                                            <td>
                                                <div className={styles.action_buttons}>
                                                    <button className={styles.action_button} title="Buy More">
                                                        <i className="fas fa-plus"></i>
                                                    </button>
                                                    <button className={styles.action_button} title="Sell">
                                                        <i className="fas fa-minus"></i>
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Two Column Layout */}
                    <div className={styles.two_column}>
                        {/* Watchlist */}
                        <div className={styles.section_card}>
                            <div className={styles.section_header}>
                                <h2>Watchlist</h2>
                                <Link href="/watchlist" className={styles.view_all}>
                                    View All <i className="fas fa-arrow-right"></i>
                                </Link>
                            </div>
                            <div className={styles.watchlist_items}>
                                {watchlist.map((item, index) => (
                                    <div key={index} className={styles.watchlist_item}>
                                        <div className={styles.watchlist_info}>
                                            <strong>{item.symbol}</strong>
                                            <span>{item.name}</span>
                                        </div>
                                        <div className={styles.watchlist_price}>
                                            <div className={styles.price}>NPR {item.price.toFixed(2)}</div>
                                            <div className={`${styles.change} ${item.change >= 0 ? styles.positive : styles.negative}`}>
                                                <i className={item.change >= 0 ? "fas fa-caret-up" : "fas fa-caret-down"}></i>
                                                {Math.abs(item.changePercent)}%
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Recent Activity */}
                        <div className={styles.section_card}>
                            <div className={styles.section_header}>
                                <h2>Recent Activity</h2>
                                <Link href="/transactions" className={styles.view_all}>
                                    View All <i className="fas fa-arrow-right"></i>
                                </Link>
                            </div>
                            <div className={styles.activity_items}>
                                {recentActivity.map((activity) => (
                                    <div key={activity.id} className={styles.activity_item}>
                                        <div className={`${styles.activity_icon} ${activity.type === 'buy' ? styles.buy : styles.sell}`}>
                                            <i className={activity.type === 'buy' ? "fas fa-arrow-up" : "fas fa-arrow-down"}></i>
                                        </div>
                                        <div className={styles.activity_info}>
                                            <div className={styles.activity_title}>
                                                <strong>{activity.type === 'buy' ? 'Bought' : 'Sold'}</strong> {activity.shares} shares of {activity.symbol}
                                            </div>
                                            <div className={styles.activity_details}>
                                                NPR {activity.price.toFixed(2)} • {activity.date} at {activity.time}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Quick Actions */}
                    <div className={styles.quick_actions}>
                        <button className={styles.action_card}>
                            <i className="fas fa-plus-circle"></i>
                            <span>Add Stock</span>
                        </button>
                        <button className={styles.action_card}>
                            <i className="fas fa-star"></i>
                            <span>Add to Watchlist</span>
                        </button>
                        <button className={styles.action_card}>
                            <i className="fas fa-download"></i>
                            <span>Export Data</span>
                        </button>
                        <button className={styles.action_card}>
                            <i className="fas fa-chart-pie"></i>
                            <span>View Analytics</span>
                        </button>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default DashboardPage;