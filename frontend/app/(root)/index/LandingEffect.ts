"use client";

import { useEffect } from "react";

export default function LandingEffects() {
    useEffect(() => {
        const nav = document.querySelector("nav");
        const navLinks = document.querySelector(".nav_links") as HTMLElement | null;

        if (!nav || !navLinks) return;

        const hamburger = document.createElement("div");
        hamburger.className = "hamburger";
        hamburger.innerHTML = "<span></span><span></span><span></span>";
        nav.appendChild(hamburger);

        const onHamburgerClick = () => {
            hamburger.classList.toggle("active");
            navLinks.classList.toggle("active");
        };
        hamburger.addEventListener("click", onHamburgerClick);

        const heroText = document.querySelector(".hero_content h1") as HTMLElement | null;
        let hue = 0;

        const heroIntervalId =
            heroText
                ? window.setInterval(() => {
                    hue = (hue + 1) % 360;

                    heroText.style.background = `linear-gradient(45deg, hsl(${hue}, 100%, 70%), hsl(${(hue + 60) % 360}, 100%, 70%))`;
                    (heroText.style as any).webkitBackgroundClip = "text";
                    heroText.style.backgroundClip = "text";
                }, 50)
                : null;

        document.querySelectorAll("h2").forEach((h2, index) => {
            if (index % 2 === 0) h2.classList.add("gradient-text");
        });

        const onScrollParallax = () => {
            const scrollPosition = window.pageYOffset;
            document.querySelectorAll<HTMLElement>("section").forEach((section, index) => {
                section.style.backgroundPositionY = `${scrollPosition * (index % 2 === 0 ? 0.3 : 0.1)}px`;
            });
        };
        window.addEventListener("scroll", onScrollParallax);

        // --- Smooth scroll for hash links ---
        const hashAnchors = Array.from(document.querySelectorAll<HTMLAnchorElement>('a[href^="#"]'));

        const onAnchorClick = (e: MouseEvent) => {
            const a = e.currentTarget as HTMLAnchorElement;
            e.preventDefault();

            if (a.classList.contains("btn")) return;

            const targetId = a.getAttribute("href");
            if (!targetId || targetId === "#") return;

            const targetElement = document.querySelector(targetId) as HTMLElement | null;
            if (!targetElement) return;

            window.scrollTo({
                top: targetElement.offsetTop - 80,
                behavior: "smooth",
            });

            hamburger.classList.remove("active");
            navLinks.classList.remove("active");
        };

        hashAnchors.forEach((a) => a.addEventListener("click", onAnchorClick));

        const animatedSelector = ".card, .company_card, .why_grid > div, .step, .testimony, .details";
        const animatedElements = Array.from(document.querySelectorAll<HTMLElement>(animatedSelector));

        animatedElements.forEach((el) => {
            el.style.opacity = "0";
            el.style.transform = "translateY(20px)";
            el.style.transition = "opacity 0.6s ease, transform 0.6s ease";
        });

        const animateOnScroll = () => {
            const windowHeight = window.innerHeight;
            animatedElements.forEach((el) => {
                const top = el.getBoundingClientRect().top;
                if (top < windowHeight - 100) {
                    el.style.opacity = "1";
                    el.style.transform = "translateY(0)";
                }
            });
        };

        window.addEventListener("scroll", animateOnScroll);
        animateOnScroll();

        const hero = document.querySelector(".hero") as HTMLElement | null;
        const particleCount = 30;
        const particles: HTMLElement[] = [];

        if (hero) {
            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement("div");
                particle.className = "particle";

                const size = Math.random() * 4 + 2;
                particle.style.width = `${size}px`;
                particle.style.height = `${size}px`;
                particle.style.left = `${Math.random() * 100}%`;
                particle.style.top = `${Math.random() * 100}%`;
                particle.style.opacity = String(Math.random() * 0.5 + 0.1);

                const duration = Math.random() * 20 + 10;
                const delay = Math.random() * 5;
                particle.style.animation = `float ${duration}s ease-in-out ${delay}s infinite`;

                hero.appendChild(particle);
                particles.push(particle);
            }
        }

        const faqItems = Array.from(document.querySelectorAll<HTMLDetailsElement>(".details"));
        const onFaqToggle = (e: Event) => {
            const current = e.currentTarget as HTMLDetailsElement;
            if (current.open) {
                faqItems.forEach((other) => {
                    if (other !== current && other.open) other.open = false;
                });
            }
        };
        faqItems.forEach((item) => item.addEventListener("toggle", onFaqToggle));

        const carousel = document.querySelector(".company-carousel") as HTMLElement | null;
        let rafId: number | null = null;
        let scrollAmount = 0;
        const scrollSpeed = 1;

        const stepScroll = () => {
            if (!carousel) return;

            const maxScroll = carousel.scrollWidth - carousel.clientWidth;
            scrollAmount += scrollSpeed;
            if (scrollAmount >= maxScroll) scrollAmount = 0;

            carousel.scrollLeft = scrollAmount;
            rafId = requestAnimationFrame(stepScroll);
        };

        const onMouseEnter = () => {
            if (!carousel) return;
            scrollAmount = carousel.scrollLeft;
            if (rafId) cancelAnimationFrame(rafId);
            rafId = null;
        };

        const onMouseLeave = () => {
            if (!carousel) return;
            if (!rafId) rafId = requestAnimationFrame(stepScroll);
        };

        if (carousel) {
            carousel.addEventListener("mouseenter", onMouseEnter);
            carousel.addEventListener("mouseleave", onMouseLeave);
            rafId = requestAnimationFrame(stepScroll);
        }

        // --- Floating elements class ---
        document.querySelectorAll(".card i, .company_card img").forEach((el) => {
            el.classList.add("floating");
        });

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) entry.target.classList.add("animate");
                });
            },
            { threshold: 0.1 }
        );

        const observeTargets = Array.from(
            document.querySelectorAll(".feature-cards .card, .company_card, .why_grid > div, .step, .testimony")
        );
        observeTargets.forEach((el) => observer.observe(el));

        return () => {
            hamburger.removeEventListener("click", onHamburgerClick);
            hamburger.remove();

            if (heroIntervalId) window.clearInterval(heroIntervalId);

            window.removeEventListener("scroll", onScrollParallax);
            window.removeEventListener("scroll", animateOnScroll);

            hashAnchors.forEach((a) => a.removeEventListener("click", onAnchorClick));
            faqItems.forEach((item) => item.removeEventListener("toggle", onFaqToggle));

            observer.disconnect();

            particles.forEach((p) => p.remove());

            if (carousel) {
                carousel.removeEventListener("mouseenter", onMouseEnter);
                carousel.removeEventListener("mouseleave", onMouseLeave);
            }
            if (rafId) cancelAnimationFrame(rafId);
        };
    }, []);

    return null;
}
