'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import styles from './navbar.module.css';

export const NavBar = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen);
    };

    // Disable scrolling when menu is open
    useEffect(() => {
        if (isMenuOpen) {
            document.body.classList.add('menu-open');
        } else {
            document.body.classList.remove('menu-open');
        }

        // Cleanup on unmount
        return () => {
            document.body.classList.remove('menu-open');
        };
    }, [isMenuOpen]);

    return (
        <>
            <div className={styles.navbar}>
                <Link href="/" className={styles.brand}>
                    <Image
                        className={styles.brand_logo}
                        src="/icon.png"
                        alt="icon"
                        width={50}
                        height={50}/>
                    <p className={styles.brand_name}>Stock Vault</p>
                </Link>

                <div className={`${styles.nav_links} ${isMenuOpen ? styles.active : ''}`}>
                    <Link href="/#features" onClick={toggleMenu}>Features</Link>
                    <Link href="/#faq" onClick={toggleMenu}>FAQ</Link>
                    <Link href="/login" onClick={toggleMenu}>Login</Link>
                </div>

                <button
                    className={styles.hamburger}
                    aria-label="Menu"
                    aria-expanded={isMenuOpen}
                    onClick={toggleMenu}
                >
                    {!isMenuOpen ? (
                        <i className="iconoir-menu"></i>
                    ) : (
                        <i className="iconoir-xmark"></i>
                    )}
                </button>
            </div>

            {isMenuOpen && (
                <div
                    className={`${styles.overlay} ${styles.active}`}
                    onClick={toggleMenu}
                ></div>
            )}
        </>
    )
}