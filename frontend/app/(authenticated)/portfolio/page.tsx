"use client"

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import styles from './portfolio.module.css';

const PortfolioPage = () => {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [showAddModal, setShowAddModal] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [sortBy, setSortBy] = useState('value');

    // Mock data - replace with actual API data
    const portfolioSummary = {
        totalInvested: 110000.00,
        currentValue: 125450.50,
        totalGain: 15450.50,
        totalGainPercent: 14.05,
        dayChange: 2345.20,
        dayChangePercent: 1.91
    };

    const holdings = [
        { id: 1, symbol: 'NABIL', name: 'Nabil Bank Ltd', sector: 'Banking', shares: 100, avgPrice: 850.00, currentPrice: 920.50, invested: 85000, value: 92050, gain: 7050, gainPercent: 8.29, allocation: 73.4 },
        { id: 2, symbol: 'NICA', name: 'NIC Asia Bank', sector: 'Banking', shares: 50, avgPrice: 720.00, currentPrice: 695.00, invested: 36000, value: 34750, gain: -1250, gainPercent: -3.47, allocation: 27.7 },
        { id: 3, symbol: 'UPPER', name: 'Upper Tamakoshi', sector: 'Hydropower', shares: 25, avgPrice: 450.00, currentPrice: 480.00, invested: 11250, value: 12000, gain: 750, gainPercent: 6.67, allocation: 9.6 },
        { id: 4, symbol: 'ADBL', name: 'Agriculture Development Bank', sector: 'Banking', shares: 30, avgPrice: 380.00, currentPrice: 385.00, invested: 11400, value: 11550, gain: 150, gainPercent: 1.32, allocation: 9.2 },
    ];

    const [addFormData, setAddFormData] = useState({
        symbol: '',
        shares: '',
        avgPrice: '',
        purchaseDate: ''
    });

    const handleAddFormChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setAddFormData({
            ...addFormData,
            [e.target.name]: e.target.value
        });
    };

    const handleAddSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Handle add stock logic here
        console.log('Adding stock:', addFormData);
        setShowAddModal(false);
        setAddFormData({ symbol: '', shares: '', avgPrice: '', purchaseDate: '' });
    };

    const filteredHoldings = holdings.filter(holding =>
        holding.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
        holding.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

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
                    <h1>Portfolio</h1>
                    <div className={styles.top_bar_actions}>
                        <button className={styles.add_stock_btn} onClick={() => setShowAddModal(true)}>
                            <i className="fas fa-plus"></i>
                            Add Stock
                        </button>
                    </div>
                </header>

                {/* Portfolio Content */}
                <div className={styles.portfolio_content}>
                    {/* Portfolio Summary */}
                    <div className={styles.summary_section}>
                        <div className={styles.summary_card_main}>
                            <div className={styles.summary_header}>
                                <div>
                                    <p className={styles.summary_label}>Total Portfolio Value</p>
                                    <h2 className={styles.summary_value}>
                                        NPR {portfolioSummary.currentValue.toLocaleString('en-NP', { minimumFractionDigits: 2 })}
                                    </h2>
                                </div>
                                <div className={styles.summary_badge}>
                                    <i className="fas fa-chart-line"></i>
                                </div>
                            </div>
                            <div className={styles.summary_details}>
                                <div className={styles.summary_item}>
                                    <span className={styles.summary_item_label}>Total Invested</span>
                                    <span className={styles.summary_item_value}>
                                        NPR {portfolioSummary.totalInvested.toLocaleString('en-NP', { minimumFractionDigits: 2 })}
                                    </span>
                                </div>
                                <div className={styles.summary_item}>
                                    <span className={styles.summary_item_label}>Total Gain/Loss</span>
                                    <span className={`${styles.summary_item_value} ${portfolioSummary.totalGain >= 0 ? styles.positive : styles.negative}`}>
                                        <i className={portfolioSummary.totalGain >= 0 ? "fas fa-arrow-up" : "fas fa-arrow-down"}></i>
                                        NPR {Math.abs(portfolioSummary.totalGain).toLocaleString('en-NP', { minimumFractionDigits: 2 })} ({portfolioSummary.totalGainPercent}%)
                                    </span>
                                </div>
                                <div className={styles.summary_item}>
                                    <span className={styles.summary_item_label}>Today's Change</span>
                                    <span className={`${styles.summary_item_value} ${portfolioSummary.dayChange >= 0 ? styles.positive : styles.negative}`}>
                                        <i className={portfolioSummary.dayChange >= 0 ? "fas fa-arrow-up" : "fas fa-arrow-down"}></i>
                                        NPR {Math.abs(portfolioSummary.dayChange).toLocaleString('en-NP', { minimumFractionDigits: 2 })} ({portfolioSummary.dayChangePercent}%)
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className={styles.allocation_card}>
                            <h3>Portfolio Allocation</h3>
                            <div className={styles.allocation_chart}>
                                {holdings.map((holding, index) => (
                                    <div
                                        key={holding.id}
                                        className={styles.allocation_item}
                                        style={{ '--item-color': `hsl(${index * 90}, 70%, 60%)` } as React.CSSProperties}
                                    >
                                        <div className={styles.allocation_bar} style={{ width: `${holding.allocation}%` }}></div>
                                        <div className={styles.allocation_info}>
                                            <span className={styles.allocation_symbol}>{holding.symbol}</span>
                                            <span className={styles.allocation_percent}>{holding.allocation}%</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Holdings Section */}
                    <div className={styles.holdings_section}>
                        <div className={styles.holdings_header}>
                            <h2>Your Holdings ({holdings.length})</h2>
                            <div className={styles.holdings_controls}>
                                <div className={styles.search_box}>
                                    <i className="fas fa-search"></i>
                                    <input
                                        type="text"
                                        placeholder="Search stocks..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                    />
                                </div>
                                <select
                                    className={styles.sort_select}
                                    value={sortBy}
                                    onChange={(e) => setSortBy(e.target.value)}
                                >
                                    <option value="value">Sort by Value</option>
                                    <option value="gain">Sort by Gain/Loss</option>
                                    <option value="symbol">Sort by Symbol</option>
                                    <option value="allocation">Sort by Allocation</option>
                                </select>
                            </div>
                        </div>

                        <div className={styles.holdings_grid}>
                            {filteredHoldings.map((holding) => (
                                <div key={holding.id} className={styles.holding_card}>
                                    <div className={styles.holding_header}>
                                        <div className={styles.holding_title}>
                                            <h3>{holding.symbol}</h3>
                                            <span className={styles.holding_sector}>{holding.sector}</span>
                                        </div>
                                        <div className={styles.holding_actions}>
                                            <button className={styles.icon_button} title="Edit">
                                                <i className="fas fa-edit"></i>
                                            </button>
                                            <button className={styles.icon_button} title="Delete">
                                                <i className="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </div>

                                    <p className={styles.holding_name}>{holding.name}</p>

                                    <div className={styles.holding_stats}>
                                        <div className={styles.stat_row}>
                                            <span className={styles.stat_label}>Shares</span>
                                            <span className={styles.stat_value}>{holding.shares}</span>
                                        </div>
                                        <div className={styles.stat_row}>
                                            <span className={styles.stat_label}>Avg Price</span>
                                            <span className={styles.stat_value}>NPR {holding.avgPrice.toFixed(2)}</span>
                                        </div>
                                        <div className={styles.stat_row}>
                                            <span className={styles.stat_label}>Current Price</span>
                                            <span className={styles.stat_value}>NPR {holding.currentPrice.toFixed(2)}</span>
                                        </div>
                                        <div className={styles.stat_row}>
                                            <span className={styles.stat_label}>Invested</span>
                                            <span className={styles.stat_value}>NPR {holding.invested.toLocaleString('en-NP')}</span>
                                        </div>
                                        <div className={styles.stat_row}>
                                            <span className={styles.stat_label}>Current Value</span>
                                            <span className={styles.stat_value}>NPR {holding.value.toLocaleString('en-NP')}</span>
                                        </div>
                                    </div>

                                    <div className={styles.holding_gain}>
                                        <div className={`${styles.gain_box} ${holding.gain >= 0 ? styles.positive : styles.negative}`}>
                                            <div className={styles.gain_amount}>
                                                <i className={holding.gain >= 0 ? "fas fa-arrow-up" : "fas fa-arrow-down"}></i>
                                                NPR {Math.abs(holding.gain).toLocaleString('en-NP')}
                                            </div>
                                            <div className={styles.gain_percent}>
                                                {Math.abs(holding.gainPercent)}%
                                            </div>
                                        </div>
                                    </div>

                                    <div className={styles.holding_footer}>
                                        <button className={styles.action_btn_primary}>
                                            <i className="fas fa-plus"></i>
                                            Buy More
                                        </button>
                                        <button className={styles.action_btn_secondary}>
                                            <i className="fas fa-chart-line"></i>
                                            View Details
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </main>

            {/* Add Stock Modal */}
            {showAddModal && (
                <div className={styles.modal_overlay} onClick={() => setShowAddModal(false)}>
                    <div className={styles.modal_content} onClick={(e) => e.stopPropagation()}>
                        <div className={styles.modal_header}>
                            <h2>Add New Stock</h2>
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
                                    value={addFormData.symbol}
                                    onChange={handleAddFormChange}
                                    placeholder="e.g., NABIL"
                                    required
                                />
                            </div>

                            <div className={styles.form_row}>
                                <div className={styles.form_group}>
                                    <label htmlFor="shares">Number of Shares</label>
                                    <input
                                        type="number"
                                        id="shares"
                                        name="shares"
                                        value={addFormData.shares}
                                        onChange={handleAddFormChange}
                                        placeholder="100"
                                        required
                                    />
                                </div>

                                <div className={styles.form_group}>
                                    <label htmlFor="avgPrice">Average Price (NPR)</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        id="avgPrice"
                                        name="avgPrice"
                                        value={addFormData.avgPrice}
                                        onChange={handleAddFormChange}
                                        placeholder="850.00"
                                        required
                                    />
                                </div>
                            </div>

                            <div className={styles.form_group}>
                                <label htmlFor="purchaseDate">Purchase Date</label>
                                <input
                                    type="date"
                                    id="purchaseDate"
                                    name="purchaseDate"
                                    value={addFormData.purchaseDate}
                                    onChange={handleAddFormChange}
                                    required
                                />
                            </div>

                            <div className={styles.modal_actions}>
                                <button type="button" className={styles.btn_cancel} onClick={() => setShowAddModal(false)}>
                                    Cancel
                                </button>
                                <button type="submit" className={styles.btn_submit}>
                                    Add Stock
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PortfolioPage;