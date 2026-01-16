"use client"

import { useState, useEffect } from 'react';
import Link from 'next/link';
import styles from './terms.module.css';

const TermsOfServicePage = () => {
    const [showBackToTop, setShowBackToTop] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setShowBackToTop(window.scrollY > 300);
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const scrollToTop = () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    return (
        <div className={styles.terms_page}>
            <div className={styles.terms_container}>
                {/* Header */}
                <div className={styles.terms_header}>
                    <h1>Terms of Service</h1>
                    <p className={styles.last_updated}>Last Updated: January 14, 2026</p>
                </div>

                {/* Content */}
                <div className={styles.terms_content}>
                    {/* Table of Contents */}
                    <div className={styles.table_of_contents}>
                        <h2>Table of Contents</h2>
                        <ul>
                            <li><a href="#agreement">1. Agreement to Terms</a></li>
                            <li><a href="#account">2. Account Registration</a></li>
                            <li><a href="#services">3. Use of Services</a></li>
                            <li><a href="#data">4. Data and Privacy</a></li>
                            <li><a href="#restrictions">5. User Restrictions</a></li>
                            <li><a href="#intellectual">6. Intellectual Property</a></li>
                            <li><a href="#disclaimer">7. Disclaimer of Warranties</a></li>
                            <li><a href="#limitation">8. Limitation of Liability</a></li>
                            <li><a href="#termination">9. Termination</a></li>
                            <li><a href="#contact">10. Contact Information</a></li>
                        </ul>
                    </div>

                    <section id="agreement" className={styles.terms_section}>
                        <h2>1. Agreement to Terms</h2>
                        <p>
                            Welcome to Stock Vault. By accessing or using our platform, you agree to be bound by these Terms of Service and all applicable laws and regulations. If you do not agree with any of these terms, you are prohibited from using or accessing this site.
                        </p>
                        <div className={styles.highlight_box}>
                            <p>
                                <strong>Important:</strong> These terms constitute a legally binding agreement between you and Stock Vault. Please read them carefully before using our services.
                            </p>
                        </div>
                        <p>
                            Stock Vault is a portfolio tracking and investment analysis platform designed for educational and informational purposes. We are a university final project aimed at helping investors in Nepal's stock market make informed decisions.
                        </p>
                    </section>

                    <section id="account" className={styles.terms_section}>
                        <h2>2. Account Registration</h2>
                        <h3>2.1 Account Creation</h3>
                        <p>
                            To access certain features of Stock Vault, you must create an account. When creating an account, you agree to:
                        </p>
                        <ul>
                            <li>Provide accurate, current, and complete information</li>
                            <li>Maintain and promptly update your account information</li>
                            <li>Keep your password secure and confidential</li>
                            <li>Accept responsibility for all activities under your account</li>
                            <li>Notify us immediately of any unauthorized access</li>
                        </ul>

                        <h3>2.2 Eligibility</h3>
                        <p>
                            You must be at least 18 years old to use Stock Vault. By creating an account, you represent and warrant that you meet this age requirement and have the legal capacity to enter into these Terms.
                        </p>

                        <h3>2.3 Account Security</h3>
                        <p>
                            You are solely responsible for maintaining the confidentiality of your account credentials. Stock Vault will not be liable for any losses arising from unauthorized use of your account.
                        </p>
                    </section>

                    <section id="services" className={styles.terms_section}>
                        <h2>3. Use of Services</h2>
                        <h3>3.1 Permitted Use</h3>
                        <p>
                            Stock Vault grants you a limited, non-exclusive, non-transferable license to access and use our platform for personal, non-commercial purposes. You may:
                        </p>
                        <ul>
                            <li>Track your investment portfolio</li>
                            <li>Monitor stock prices and trends</li>
                            <li>Analyze historical market data</li>
                            <li>Create and manage your wishlist of companies</li>
                            <li>Access educational resources and analytics</li>
                        </ul>

                        <h3>3.2 Service Availability</h3>
                        <p>
                            While we strive to maintain continuous service availability, Stock Vault does not guarantee uninterrupted access. We reserve the right to modify, suspend, or discontinue any aspect of the service at any time without prior notice.
                        </p>

                        <div className={styles.warning_box}>
                            <p>
                                <strong>Investment Disclaimer:</strong> Stock Vault is for informational purposes only. We do not provide investment advice, and the information on our platform should not be considered as such. Always conduct your own research and consult with financial professionals before making investment decisions.
                            </p>
                        </div>
                    </section>

                    <section id="data" className={styles.terms_section}>
                        <h2>4. Data and Privacy</h2>
                        <h3>4.1 Data Collection</h3>
                        <p>
                            We collect and process your personal data in accordance with our <Link href="/privacy">Privacy Policy</Link>. By using Stock Vault, you consent to such collection and processing.
                        </p>

                        <h3>4.2 Your Data Rights</h3>
                        <p>You have the right to:</p>
                        <ul>
                            <li>Access your personal data</li>
                            <li>Request correction of inaccurate data</li>
                            <li>Request deletion of your data</li>
                            <li>Export your portfolio data</li>
                            <li>Opt-out of marketing communications</li>
                        </ul>

                        <h3>4.3 Data Security</h3>
                        <p>
                            We implement industry-standard security measures to protect your data. However, no method of transmission over the internet is 100% secure, and we cannot guarantee absolute security.
                        </p>
                    </section>

                    <section id="restrictions" className={styles.terms_section}>
                        <h2>5. User Restrictions</h2>
                        <p>When using Stock Vault, you agree NOT to:</p>
                        <ol>
                            <li>Violate any applicable laws or regulations</li>
                            <li>Infringe upon the rights of others</li>
                            <li>Transmit harmful code, viruses, or malware</li>
                            <li>Attempt to gain unauthorized access to our systems</li>
                            <li>Use automated scripts or bots to access the platform</li>
                            <li>Reverse engineer or attempt to extract source code</li>
                            <li>Use the service for any illegal or fraudulent activity</li>
                            <li>Share false or misleading information</li>
                            <li>Harass, abuse, or harm other users</li>
                            <li>Sell, transfer, or sublicense your account</li>
                        </ol>
                        <p>
                            Violation of these restrictions may result in immediate termination of your account and potential legal action.
                        </p>
                    </section>

                    <section id="intellectual" className={styles.terms_section}>
                        <h2>6. Intellectual Property</h2>
                        <h3>6.1 Our Property</h3>
                        <p>
                            All content, features, and functionality of Stock Vault, including but not limited to text, graphics, logos, icons, images, software, and data compilations, are the exclusive property of Stock Vault and are protected by copyright, trademark, and other intellectual property laws.
                        </p>

                        <h3>6.2 User Content</h3>
                        <p>
                            You retain ownership of any data or information you input into Stock Vault. By using our service, you grant us a limited license to use, store, and process this data solely for the purpose of providing our services to you.
                        </p>

                        <h3>6.3 Feedback</h3>
                        <p>
                            Any feedback, suggestions, or ideas you provide to Stock Vault may be used by us without any obligation to compensate you.
                        </p>
                    </section>

                    <section id="disclaimer" className={styles.terms_section}>
                        <h2>7. Disclaimer of Warranties</h2>
                        <div className={styles.warning_box}>
                            <p>
                                <strong>Stock Vault is provided "AS IS" and "AS AVAILABLE" without warranties of any kind, either express or implied.</strong>
                            </p>
                        </div>
                        <p>We specifically disclaim:</p>
                        <ul>
                            <li>Warranties of merchantability or fitness for a particular purpose</li>
                            <li>Guarantees of accuracy, completeness, or timeliness of data</li>
                            <li>Assurances that the service will be error-free or uninterrupted</li>
                            <li>Responsibility for third-party data or market information</li>
                        </ul>
                        <p>
                            <strong>Investment Risk Notice:</strong> Stock market investments carry inherent risks. Past performance does not guarantee future results. Stock Vault is not responsible for any investment losses you may incur.
                        </p>
                    </section>

                    <section id="limitation" className={styles.terms_section}>
                        <h2>8. Limitation of Liability</h2>
                        <p>
                            To the maximum extent permitted by law, Stock Vault and its developers shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including but not limited to:
                        </p>
                        <ul>
                            <li>Loss of profits or investment losses</li>
                            <li>Loss of data or business interruption</li>
                            <li>Personal injury or property damage</li>
                            <li>Unauthorized access to your account</li>
                            <li>Errors or omissions in market data</li>
                        </ul>
                        <p>
                            Our total liability for any claims related to Stock Vault shall not exceed the amount you paid to us in the 12 months preceding the claim (if any).
                        </p>
                    </section>

                    <section id="termination" className={styles.terms_section}>
                        <h2>9. Termination</h2>
                        <h3>9.1 Termination by You</h3>
                        <p>
                            You may terminate your account at any time by contacting us or using the account deletion feature in your settings. Upon termination, your right to access the service will immediately cease.
                        </p>

                        <h3>9.2 Termination by Us</h3>
                        <p>
                            We reserve the right to suspend or terminate your account at our sole discretion, without prior notice, for conduct that we believe:
                        </p>
                        <ul>
                            <li>Violates these Terms of Service</li>
                            <li>Is harmful to other users or Stock Vault</li>
                            <li>Exposes us to liability</li>
                            <li>Is fraudulent or illegal</li>
                        </ul>

                        <h3>9.3 Effect of Termination</h3>
                        <p>
                            Upon termination, all licenses and rights granted to you will immediately cease. You may request a copy of your data within 30 days of termination.
                        </p>
                    </section>

                    <section id="contact" className={styles.terms_section}>
                        <h2>10. Governing Law and Dispute Resolution</h2>
                        <p>
                            These Terms shall be governed by and construed in accordance with the laws of Nepal. Any disputes arising from these Terms or your use of Stock Vault shall be resolved through binding arbitration in accordance with Nepalese law.
                        </p>

                        <h3>Changes to Terms</h3>
                        <p>
                            We reserve the right to modify these Terms at any time. We will notify users of significant changes via email or through the platform. Your continued use of Stock Vault after such modifications constitutes acceptance of the updated Terms.
                        </p>
                    </section>

                    <div className={styles.contact_section}>
                        <h3>Questions About These Terms?</h3>
                        <p>
                            If you have any questions or concerns about these Terms of Service, please don't hesitate to contact us.
                        </p>
                        <Link href="/#contact" className={styles.contact_button}>
                            Contact Us
                        </Link>
                    </div>
                </div>
            </div>

            <button
                className={`${styles.back_to_top} ${showBackToTop ? styles.visible : ''}`}
                onClick={scrollToTop}
                aria-label="Back to top"
            >
                <i className="fas fa-arrow-up"></i>
            </button>
        </div>
    );
};

export default TermsOfServicePage;