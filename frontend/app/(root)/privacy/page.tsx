"use client"

import { useState, useEffect } from 'react';
import Link from 'next/link';
import styles from './privacy.module.css';

const PrivacyPolicyPage = () => {
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
        <div className={styles.privacy_page}>
            <div className={styles.privacy_container}>
                <div className={styles.privacy_header}>
                    <h1>Privacy Policy</h1>
                    <p className={styles.last_updated}>Last Updated: January 14, 2026</p>
                </div>

                <div className={styles.privacy_content}>
                    <div className={styles.privacy_intro}>
                        <p>
                            At Stock Vault, we take your privacy seriously. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our portfolio tracking and investment analysis platform. Please read this policy carefully to understand our practices regarding your personal data.
                        </p>
                    </div>

                    <div className={styles.table_of_contents}>
                        <h2>Table of Contents</h2>
                        <ul>
                            <li><a href="#collection">1. Information We Collect</a></li>
                            <li><a href="#usage">2. How We Use Your Information</a></li>
                            <li><a href="#sharing">3. How We Share Your Information</a></li>
                            <li><a href="#cookies">4. Cookies and Tracking</a></li>
                            <li><a href="#security">5. Data Security</a></li>
                            <li><a href="#rights">6. Your Privacy Rights</a></li>
                            <li><a href="#retention">7. Data Retention</a></li>
                            <li><a href="#children">8. Children's Privacy</a></li>
                            <li><a href="#international">9. International Data Transfers</a></li>
                            <li><a href="#changes">10. Changes to This Policy</a></li>
                            <li><a href="#contact">11. Contact Us</a></li>
                        </ul>
                    </div>

                    <section id="collection" className={`${styles.privacy_section} ${styles.section}`}>
                        <h2>1. Information We Collect</h2>

                        <h3>1.1 Information You Provide</h3>
                        <p>We collect information that you voluntarily provide to us when you:</p>
                        <ul>
                            <li><strong>Create an account:</strong> Name, email address, password</li>
                            <li><strong>Use our services:</strong> Portfolio data, stock holdings, wishlist items</li>
                            <li><strong>Contact us:</strong> Messages, feedback, support inquiries</li>
                            <li><strong>Participate in surveys:</strong> Opinions, preferences, feedback</li>
                        </ul>

                        <h3>1.2 Information Collected Automatically</h3>
                        <p>When you access Stock Vault, we automatically collect certain information:</p>

                        <div className={styles.highlight_box}>
                            <ul>
                                <li><strong>Device Information:</strong> IP address, browser type, operating system, device identifiers</li>
                                <li><strong>Usage Data:</strong> Pages visited, features used, time spent, click patterns</li>
                                <li><strong>Location Data:</strong> General geographic location based on IP address</li>
                                <li><strong>Log Data:</strong> Access times, error logs, performance metrics</li>
                            </ul>
                        </div>

                        <h3>1.3 Information from Third Parties</h3>
                        <p>We may receive information from third-party sources, including:</p>
                        <ul>
                            <li>Stock market data providers for real-time pricing</li>
                            <li>Social media platforms if you connect your account</li>
                            <li>Analytics providers for usage insights</li>
                            <li>Payment processors for transaction information</li>
                        </ul>
                    </section>

                    <section id="usage" className={`${styles.privacy_section} ${styles.section}`}>
                        <h2>2. How We Use Your Information</h2>

                        <p>We use the information we collect for the following purposes:</p>

                        <h3>2.1 To Provide Our Services</h3>
                        <ul>
                            <li>Create and manage your account</li>
                            <li>Track your investment portfolio</li>
                            <li>Display stock prices and market data</li>
                            <li>Generate analytics and insights</li>
                            <li>Provide customer support</li>
                        </ul>

                        <h3>2.2 To Improve Our Platform</h3>
                        <ul>
                            <li>Analyze usage patterns and trends</li>
                            <li>Develop new features and functionality</li>
                            <li>Fix bugs and optimize performance</li>
                            <li>Conduct research and testing</li>
                        </ul>

                        <h3>2.3 To Communicate With You</h3>
                        <ul>
                            <li>Send service updates and notifications</li>
                            <li>Respond to your inquiries and requests</li>
                            <li>Send marketing communications (with your consent)</li>
                            <li>Provide important security alerts</li>
                        </ul>

                        <h3>2.4 To Ensure Security</h3>
                        <ul>
                            <li>Detect and prevent fraud and abuse</li>
                            <li>Monitor for suspicious activity</li>
                            <li>Enforce our Terms of Service</li>
                            <li>Protect user safety and data integrity</li>
                        </ul>

                        <div className={styles.info_box}>
                            <p>
                                <strong>Note:</strong> Stock Vault is for informational purposes only. We do not use your data to provide investment advice or make trading decisions on your behalf.
                            </p>
                        </div>
                    </section>

                    <section id="sharing" className={`${styles.privacy_section} ${styles.section}`}>
                        <h2>3. How We Share Your Information</h2>

                        <p>We do not sell your personal information. We may share your information in the following circumstances:</p>

                        <h3>3.1 Service Providers</h3>
                        <p>We share data with third-party service providers who perform services on our behalf:</p>
                        <ul>
                            <li>Cloud hosting providers (data storage)</li>
                            <li>Analytics services (usage tracking)</li>
                            <li>Email service providers (communications)</li>
                            <li>Payment processors (if applicable)</li>
                            <li>Customer support tools</li>
                        </ul>

                        <h3>3.2 Legal Requirements</h3>
                        <p>We may disclose your information if required to do so by law or in response to:</p>
                        <ul>
                            <li>Valid legal processes (subpoenas, court orders)</li>
                            <li>Government or regulatory requests</li>
                            <li>Protection of our legal rights</li>
                            <li>Emergency situations involving safety</li>
                        </ul>

                        <h3>3.3 Business Transfers</h3>
                        <p>
                            If Stock Vault is involved in a merger, acquisition, or sale of assets, your information may be transferred as part of that transaction. We will notify you before your information is transferred and becomes subject to a different privacy policy.
                        </p>

                        <h3>3.4 With Your Consent</h3>
                        <p>
                            We may share your information for any other purpose with your explicit consent.
                        </p>
                    </section>

                    <section id="cookies" className={`${styles.privacy_section} ${styles.section}`}>
                        <h2>4. Cookies and Tracking Technologies</h2>

                        <h3>4.1 What Are Cookies?</h3>
                        <p>
                            Cookies are small text files placed on your device to store data that can be recalled by a web server. We use cookies and similar tracking technologies to track activity on our platform and store certain information.
                        </p>

                        <h3>4.2 Types of Cookies We Use</h3>

                        <table className={styles.data_table}>
                            <thead>
                                <tr>
                                    <th>Cookie Type</th>
                                    <th>Purpose</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>Essential Cookies</strong></td>
                                    <td>Required for basic platform functionality and security</td>
                                </tr>
                                <tr>
                                    <td><strong>Performance Cookies</strong></td>
                                    <td>Help us understand how visitors interact with our platform</td>
                                </tr>
                                <tr>
                                    <td><strong>Functional Cookies</strong></td>
                                    <td>Remember your preferences and settings</td>
                                </tr>
                                <tr>
                                    <td><strong>Targeting Cookies</strong></td>
                                    <td>Deliver relevant content and advertisements</td>
                                </tr>
                            </tbody>
                        </table>

                        <h3>4.3 Managing Cookies</h3>
                        <p>
                            You can control cookies through your browser settings. However, disabling cookies may limit your ability to use certain features of Stock Vault.
                        </p>

                        <div className={styles.highlight_box}>
                            <p>
                                <strong>Third-Party Tracking:</strong> We use Google Analytics to analyze platform usage. You can opt-out of Google Analytics by installing the Google Analytics opt-out browser add-on.
                            </p>
                        </div>
                    </section>

                    <section id="security" className={`${styles.privacy_section} ${styles.section}`}>
                        <h2>5. Data Security</h2>

                        <h3>5.1 Our Security Measures</h3>
                        <p>We implement industry-standard security measures to protect your data:</p>
                        <ul>
                            <li><strong>Encryption:</strong> All data transmission uses SSL/TLS encryption</li>
                            <li><strong>Access Controls:</strong> Strict access limitations to personal data</li>
                            <li><strong>Regular Audits:</strong> Periodic security assessments and penetration testing</li>
                            <li><strong>Secure Storage:</strong> Encrypted databases and secure cloud infrastructure</li>
                            <li><strong>Password Protection:</strong> Passwords are hashed using bcrypt</li>
                        </ul>

                        <h3>5.2 Your Responsibility</h3>
                        <p>While we take security seriously, you also play a role in protecting your data:</p>
                        <ul>
                            <li>Use a strong, unique password</li>
                            <li>Enable two-factor authentication if available</li>
                            <li>Keep your login credentials confidential</li>
                            <li>Log out after using shared devices</li>
                            <li>Report suspicious activity immediately</li>
                        </ul>

                        <div className={styles.warning_box}>
                            <p>
                                <strong>Important:</strong> No method of transmission over the internet is 100% secure. While we strive to protect your data, we cannot guarantee absolute security. Use Stock Vault at your own risk.
                            </p>
                        </div>
                    </section>

                    <section id="rights" className={`${styles.privacy_section} ${styles.section}`}>
                        <h2>6. Your Privacy Rights</h2>

                        <p>Depending on your location, you may have certain rights regarding your personal data:</p>

                        <h3>6.1 Access and Portability</h3>
                        <ul>
                            <li><strong>Right to Access:</strong> Request a copy of your personal data</li>
                            <li><strong>Right to Portability:</strong> Receive your data in a structured, machine-readable format</li>
                        </ul>

                        <h3>6.2 Correction and Deletion</h3>
                        <ul>
                            <li><strong>Right to Correct:</strong> Update inaccurate or incomplete data</li>
                            <li><strong>Right to Delete:</strong> Request deletion of your personal data</li>
                        </ul>

                        <h3>6.3 Restriction and Objection</h3>
                        <ul>
                            <li><strong>Right to Restrict:</strong> Limit how we process your data</li>
                            <li><strong>Right to Object:</strong> Object to processing for specific purposes</li>
                        </ul>

                        <h3>6.4 Marketing Communications</h3>
                        <ul>
                            <li><strong>Opt-Out:</strong> Unsubscribe from marketing emails at any time</li>
                            <li><strong>Preferences:</strong> Manage your communication preferences in account settings</li>
                        </ul>

                        <div className={styles.highlight_box}>
                            <p>
                                <strong>How to Exercise Your Rights:</strong> To exercise any of these rights, please contact us at <a href="mailto:privacy@stockvault.com">privacy@stockvault.com</a> or use the contact form on our website. We will respond to your request within 30 days.
                            </p>
                        </div>
                    </section>

                    <section id="retention" className={`${styles.privacy_section} ${styles.section}`}>
                        <h2>7. Data Retention</h2>

                        <p>
                            We retain your personal data only for as long as necessary to fulfill the purposes outlined in this Privacy Policy, unless a longer retention period is required by law.
                        </p>

                        <h3>7.1 Retention Periods</h3>
                        <ul>
                            <li><strong>Account Data:</strong> Retained while your account is active</li>
                            <li><strong>Portfolio Data:</strong> Retained for the duration of your account</li>
                            <li><strong>Usage Logs:</strong> Retained for up to 12 months</li>
                            <li><strong>Support Communications:</strong> Retained for up to 3 years</li>
                        </ul>

                        <h3>7.2 Account Deletion</h3>
                        <p>
                            When you delete your account, we will delete or anonymize your personal data within 30 days, except where we are required to retain it for legal or regulatory purposes.
                        </p>
                    </section>

                    <section id="children" className={`${styles.privacy_section} ${styles.section}`}>
                        <h2>8. Children's Privacy</h2>

                        <p>
                            Stock Vault is not intended for children under the age of 18. We do not knowingly collect personal information from children under 18. If you are a parent or guardian and believe your child has provided us with personal information, please contact us immediately.
                        </p>

                        <p>
                            If we discover that we have collected personal information from a child under 18, we will delete that information as quickly as possible.
                        </p>
                    </section>

                    <section id="international" className={`${styles.privacy_section} ${styles.section}`}>
                        <h2>9. International Data Transfers</h2>

                        <p>
                            Your information may be transferred to and processed in countries other than your country of residence. These countries may have data protection laws that are different from the laws of your country.
                        </p>

                        <p>
                            When we transfer your data internationally, we ensure appropriate safeguards are in place to protect your information in accordance with this Privacy Policy.
                        </p>

                        <div className={styles.info_box}>
                            <p>
                                <strong>Data Location:</strong> Stock Vault's primary servers are located in [Your Server Location]. By using our services, you consent to the transfer of your data to these locations.
                            </p>
                        </div>
                    </section>

                    <section id="changes" className={`${styles.privacy_section} ${styles.section}`}>
                        <h2>10. Changes to This Privacy Policy</h2>

                        <p>
                            We may update this Privacy Policy from time to time to reflect changes in our practices or for other operational, legal, or regulatory reasons.
                        </p>

                        <h3>10.1 Notification of Changes</h3>
                        <p>When we make material changes to this policy, we will:</p>
                        <ul>
                            <li>Update the "Last Updated" date at the top of this page</li>
                            <li>Notify you via email (if you have provided one)</li>
                            <li>Display a prominent notice on our platform</li>
                            <li>Request your consent for significant changes (where required by law)</li>
                        </ul>

                        <h3>10.2 Your Continued Use</h3>
                        <p>
                            Your continued use of Stock Vault after any changes to this Privacy Policy constitutes your acceptance of the updated policy.
                        </p>
                    </section>

                    <section id="contact" className={`${styles.privacy_section} ${styles.section}`}>
                        <h2>11. Additional Information</h2>

                        <h3>11.1 California Privacy Rights</h3>
                        <p>
                            If you are a California resident, you have additional rights under the California Consumer Privacy Act (CCPA), including the right to know what personal information we collect and how we use it.
                        </p>

                        <h3>11.2 European Privacy Rights</h3>
                        <p>
                            If you are in the European Economic Area (EEA), you have rights under the General Data Protection Regulation (GDPR), including the right to lodge a complaint with a supervisory authority.
                        </p>

                        <h3>11.3 Do Not Track</h3>
                        <p>
                            Some browsers include a "Do Not Track" (DNT) feature. Currently, there is no industry standard for how to respond to DNT signals, and Stock Vault does not respond to DNT signals at this time.
                        </p>
                    </section>

                    <div className={styles.contact_section}>
                        <h3>Questions About Privacy?</h3>
                        <p>
                            If you have any questions, concerns, or requests regarding this Privacy Policy or our data practices, please contact us:
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

export default PrivacyPolicyPage;