"use client"

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import styles from './watchlist.module.css';

const WatchlistPage = () => {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [showAddModal, setShowAddModal] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [sortBy, setSortBy] = useState('change');
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

    // Mock data - replace with actual API data
    const marketOverview = {
        nepse: 2145.67,
        nepseChange: 15.23,
        nepseChangePercent: 0.71,
        totalTurnover: 3245678900,
        totalTransactions: 45678
    };

    const watchlistStocks = [
        { id: 1, symbol: 'NABIL', name: 'Nabil Bank Ltd', sector: 'Banking', price: 920.50, open: 915.00, high: 925.00, low: 912.50, change: 5.50, changePercent: 0.60, volume: 12500, marketCap: 45678000000, pe: 15.6, isGainer: true },
        { id: 2, symbol: 'NICA', name: 'NIC Asia Bank', sector: 'Banking', price: 695.00, open: 700.00, high: 705.00, low: 690.00, change: -5.00, changePercent: -0.71, volume: 8900, marketCap: 34567000000, pe: 13.2, isGainer: false },
        { id: 3, symbol: 'UPPER', name: 'Upper Tamakoshi', sector: 'Hydropower', price: 480.00, open: 475.00, high: 485.00, low: 473.00, change: 5.00, changePercent: 1.05, volume: 5600, marketCap: 23456000000, pe: 18.9, isGainer: true },
        { id: 4, symbol: 'ADBL', name: 'Agriculture Development Bank', sector: 'Banking', price: 385.00, open: 380.00, high: 388.00, low: 378.00, change: 5.00, changePercent: 1.32, volume: 15000, marketCap: 15678000000, pe: 12.4, isGainer: true },
        { id: 5, symbol: 'HIDCL', name: 'Hydroelectricity Investment', sector: 'Hydropower', price: 295.50, open: 298.00, high: 300.00, low: 294.00, change: -2.50, changePercent: -0.84, volume: 7800, marketCap: 12345000000, pe: 16.7, isGainer: false },
        { id: 6, symbol: 'NLIC', name: 'Nepal Life Insurance', sector: 'Insurance', price: 1250.00, open: 1235.00, high: 1255.00, low: 1230.00, change: 15.00, changePercent: 1.22, volume: 3400, marketCap: 28900000000, pe: 20.3, isGainer: true },
    ];

    const [addSymbol, setAddSymbol] = useState('');

    const handleAddSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Handle add to watchlist logic here
        console.log('Adding to watchlist:', addSymbol);
        setShowAddModal(false);
        setAddSymbol('');
    };

    const handleRemoveStock = (id: number) => {
        // Handle remove from watchlist
        console.log('Removing stock:', id);
    };

    const filteredStocks = watchlistStocks.filter(stock =>
        stock.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
        stock.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className={styles.dashboard}>
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
                    <Link href="/dashboard" className={styles.nav_item}>
                        <i className="fas fa-chart-line"></i>
                        <span>Dashboard</span>
                    </Link>
                    <Link href="/portfolio" className={styles.nav_item}>
                        <i className="fas fa-briefcase"></i>
                        <span>Portfolio</span>
                    </Link>
                    <Link href="/watchlist" className={styles.nav_item_active}>
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
                            <i className="fas fa-user"></i>
                        </div>
                        <div className={styles.user_info}>
                            <p className={styles.user_name}>John Doe</p>
                            <p className={styles.user_email}>john@example.com</p>
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
                    <h1>Watchlist</h1>
                    <div className={styles.top_bar_actions}>
                        <button className={styles.add_stock_btn} onClick={() => setShowAddModal(true)}>
                            <i className="fas fa-plus"></i>
                            Add to Watchlist
                        </button>
                    </div>
                </header>

                {/* Watchlist Content */}
                <div className={styles.watchlist_content}>
                    {/* Market Overview */}
                    <div className={styles.market_overview}>
                        <div className={styles.market_card}>
                            <div className={styles.market_icon}>
                                <i className="fas fa-chart-area"></i>
                            </div>
                            <div className={styles.market_info}>
                                <p className={styles.market_label}>NEPSE Index</p>
                                <h3 className={styles.market_value}>{marketOverview.nepse.toFixed(2)}</h3>
                                <p className={`${styles.market_change} ${marketOverview.nepseChange >= 0 ? styles.positive : styles.negative}`}>
                                    <i className={marketOverview.nepseChange >= 0 ? "fas fa-arrow-up" : "fas fa-arrow-down"}></i>
                                    {Math.abs(marketOverview.nepseChange).toFixed(2)} ({Math.abs(marketOverview.nepseChangePercent)}%)
                                </p>
                            </div>
                        </div>

                        <div className={styles.market_card}>
                            <div className={styles.market_icon}>
                                <i className="fas fa-coins"></i>
                            </div>
                            <div className={styles.market_info}>
                                <p className={styles.market_label}>Total Turnover</p>
                                <h3 className={styles.market_value}>NPR {(marketOverview.totalTurnover / 1000000).toFixed(2)}M</h3>
                                <p className={styles.market_subtitle}>{marketOverview.totalTransactions.toLocaleString()} transactions</p>
                            </div>
                        </div>

                        <div className={styles.market_card}>
                            <div className={styles.market_icon}>
                                <i className="fas fa-eye"></i>
                            </div>
                            <div className={styles.market_info}>
                                <p className={styles.market_label}>Watching</p>
                                <h3 className={styles.market_value}>{watchlistStocks.length}</h3>
                                <p className={styles.market_subtitle}>stocks in watchlist</p>
                            </div>
                        </div>
                    </div>

                    {/* Controls */}
                    <div className={styles.controls_section}>
                        <div className={styles.search_box}>
                            <i className="fas fa-search"></i>
                            <input
                                type="text"
                                placeholder="Search watchlist..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>

                        <div className={styles.controls_right}>
                            <select
                                className={styles.sort_select}
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value)}
                            >
                                <option value="change">Sort by Change</option>
                                <option value="price">Sort by Price</option>
                                <option value="volume">Sort by Volume</option>
                                <option value="symbol">Sort by Symbol</option>
                            </select>

                            <div className={styles.view_toggle}>
                                <button
                                    className={`${styles.view_btn} ${viewMode === 'grid' ? styles.active : ''}`}
                                    onClick={() => setViewMode('grid')}
                                >
                                    <i className="fas fa-th"></i>
                                </button>
                                <button
                                    className={`${styles.view_btn} ${viewMode === 'list' ? styles.active : ''}`}
                                    onClick={() => setViewMode('list')}
                                >
                                    <i className="fas fa-list"></i>
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Stocks Display */}
                    <div className={viewMode === 'grid' ? styles.stocks_grid : styles.stocks_list}>
                        {filteredStocks.map((stock) => (
                            <div key={stock.id} className={viewMode === 'grid' ? styles.stock_card : styles.stock_row}>
                                <div className={styles.stock_header}>
                                    <div className={styles.stock_title}>
                                        <h3>{stock.symbol}</h3>
                                        {stock.isGainer && <span className={styles.gainer_badge}>Top Gainer</span>}
                                    </div>
                                    <button
                                        className={styles.remove_btn}
                                        onClick={() => handleRemoveStock(stock.id)}
                                        title="Remove from watchlist"
                                    >
                                        <i className="fas fa-star"></i>
                                    </button>
                                </div>

                                <p className={styles.stock_name}>{stock.name}</p>
                                <span className={styles.stock_sector}>{stock.sector}</span>

                                <div className={styles.price_section}>
                                    <div className={styles.current_price}>
                                        <span className={styles.price_label}>Current Price</span>
                                        <h2 className={styles.price_value}>NPR {stock.price.toFixed(2)}</h2>
                                    </div>
                                    <div className={`${styles.price_change} ${stock.change >= 0 ? styles.positive : styles.negative}`}>
                                        <i className={stock.change >= 0 ? "fas fa-caret-up" : "fas fa-caret-down"}></i>
                                        <span>{Math.abs(stock.change).toFixed(2)} ({Math.abs(stock.changePercent)}%)</span>
                                    </div>
                                </div>

                                <div className={styles.stock_details}>
                                    <div className={styles.detail_item}>
                                        <span className={styles.detail_label}>Open</span>
                                        <span className={styles.detail_value}>NPR {stock.open.toFixed(2)}</span>
                                    </div>
                                    <div className={styles.detail_item}>
                                        <span className={styles.detail_label}>High</span>
                                        <span className={styles.detail_value}>NPR {stock.high.toFixed(2)}</span>
                                    </div>
                                    <div className={styles.detail_item}>
                                        <span className={styles.detail_label}>Low</span>
                                        <span className={styles.detail_value}>NPR {stock.low.toFixed(2)}</span>
                                    </div>
                                    <div className={styles.detail_item}>
                                        <span className={styles.detail_label}>Volume</span>
                                        <span className={styles.detail_value}>{stock.volume.toLocaleString()}</span>
                                    </div>
                                    <div className={styles.detail_item}>
                                        <span className={styles.detail_label}>P/E Ratio</span>
                                        <span className={styles.detail_value}>{stock.pe}</span>
                                    </div>
                                    <div className={styles.detail_item}>
                                        <span className={styles.detail_label}>Market Cap</span>
                                        <span className={styles.detail_value}>NPR {(stock.marketCap / 1000000000).toFixed(2)}B</span>
                                    </div>
                                </div>

                                <div className={styles.stock_actions}>
                                    <button className={styles.action_btn_primary}>
                                        <i className="fas fa-plus-circle"></i>
                                        Add to Portfolio
                                    </button>
                                    <button className={styles.action_btn_secondary}>
                                        <i className="fas fa-chart-line"></i>
                                        View Chart
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>

                    {filteredStocks.length === 0 && (
                        <div className={styles.empty_state}>
                            <i className="fas fa-star"></i>
                            <h3>No stocks in your watchlist</h3>
                            <p>Start adding stocks to track their performance</p>
                            <button className={styles.add_stock_btn} onClick={() => setShowAddModal(true)}>
                                <i className="fas fa-plus"></i>
                                Add Stock
                            </button>
                        </div>
                    )}
                </div>
            </main>

            {/* Add to Watchlist Modal */}
            {showAddModal && (
                <div className={styles.modal_overlay} onClick={() => setShowAddModal(false)}>
                    <div className={styles.modal_content} onClick={(e) => e.stopPropagation()}>
                        <div className={styles.modal_header}>
                            <h2>Add to Watchlist</h2>
                            <button className={styles.modal_close} onClick={() => setShowAddModal(false)}>
                                <i className="fas fa-times"></i>
                            </button>
                        </div>

                        <form onSubmit={handleAddSubmit} className={styles.add_form}>
                            <div className={styles.form_group}>
                                <label htmlFor="symbol">Stock Symbol</label>
                                <input
                                    type="text"
                                    id="symbol"
                                    name="symbol"
                                    value={addSymbol}
                                    onChange={(e) => setAddSymbol(e.target.value)}
                                    placeholder="e.g., NABIL, NICA, UPPER"
                                    required
                                />
                                <p className={styles.form_hint}>Enter the stock symbol you want to watch</p>
                            </div>

                            <div className={styles.modal_actions}>
                                <button type="button" className={styles.btn_cancel} onClick={() => setShowAddModal(false)}>
                                    Cancel
                                </button>
                                <button type="submit" className={styles.btn_submit}>
                                    Add to Watchlist
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default WatchlistPage;