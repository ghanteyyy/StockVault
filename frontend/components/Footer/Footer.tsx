import Link from "next/link";
import styles from "./Footer.module.css";


export default function Footer() {
    return (
        <div className={styles.footer}>
            <div className={styles.footer_content}>
                <div className={`${styles.footer_section} ${styles.footer_brand}`}>
                    <h4>Stock Vault</h4>
                    <p>Track stocks, seize profits, vibe smart.</p>
                </div>

                <div className={`${styles.footer_section} ${styles.footer_links}`}>
                    <h4>Explore</h4>

                    <div className={styles.links}>
                        <Link href="/">Home</Link>
                        <Link href="/#features">Features</Link>
                        <Link href="/#faq">FAQ</Link>
                        <Link href="/login">Login</Link>
                    </div>
                </div>

                <div className={`${styles.footer_section} ${styles.footer_newsletter}`}>
                    <h4>Stay Updated</h4>

                    <div className={styles.social_icons}>
                        <Link
                            href="https://twitter.com"
                            target="_blank"
                            aria-label="Twitter">

                            <i className="fab fa-twitter" />
                        </Link>

                        <Link
                            href="https://linkedin.com"
                            target="_blank"
                            aria-label="LinkedIn">

                            <i className="fab fa-linkedin" />
                        </Link>

                        <Link
                            href="https://www.github.com/ghanteyyy/"
                            target="_blank"
                            aria-label="GitHub"
                            rel="noopener noreferrer">

                            <i className="fab fa-github" />
                        </Link>
                    </div>
                </div>
            </div>

            <div className={styles.footer_bottom}>
                <p>&copy; {new Date().getFullYear()} Stock Vault. All rights reserved.</p>
            </div>
        </div>
    );
}
