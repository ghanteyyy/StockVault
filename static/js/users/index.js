document.addEventListener('DOMContentLoaded', function () {
    const hamburger = document.createElement('div');
    hamburger.className = 'hamburger';
    hamburger.innerHTML = '<span></span><span></span><span></span>';
    document.querySelector('nav').appendChild(hamburger);

    const navLinks = document.querySelector('.nav-links');

    hamburger.addEventListener('click', function () {
        this.classList.toggle('active');
        navLinks.classList.toggle('active');
    });

    const heroText = document.querySelector('.hero-content h1');
    if (heroText) {
        let hue = 0;
        setInterval(() => {
            hue = (hue + 1) % 360;
            heroText.style.background = `linear-gradient(45deg, hsl(${hue}, 100%, 70%), hsl(${(hue + 60) % 360}, 100%, 70%))`;
            heroText.style.webkitBackgroundClip = 'text';
            heroText.style.backgroundClip = 'text';
        }, 50);
    }

    document.querySelectorAll('h2').forEach((h2, index) => {
        if (index % 2 === 0) {
            h2.classList.add('gradient-text');
        }
    });

    window.addEventListener('scroll', function () {
        const scrollPosition = window.pageYOffset;
        document.querySelectorAll('section').forEach((section, index) => {
            if (index % 2 === 0) {
                section.style.backgroundPositionY = `${scrollPosition * 0.3}px`;
            } else {
                section.style.backgroundPositionY = `${scrollPosition * 0.1}px`;
            }
        });
    });

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            if (this.classList.contains('btn')) return;
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            }
        });
    });

    const animateOnScroll = function () {
        const elements = document.querySelectorAll('.card, .company-card, .why-grid > div, .step, .testimony, details');
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            if (elementPosition < windowHeight - 100) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };

    const animatedElements = document.querySelectorAll('.card, .company-card, .why-grid > div, .step, .testimony, details');
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });

    const createParticles = function () {
        const hero = document.querySelector('.hero');
        const particleCount = 30;
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            const size = Math.random() * 4 + 2;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.top = `${Math.random() * 100}%`;
            particle.style.opacity = Math.random() * 0.5 + 0.1;
            const duration = Math.random() * 20 + 10;
            const delay = Math.random() * 5;
            particle.style.animation = `float ${duration}s ease-in-out ${delay}s infinite`;
            hero.appendChild(particle);
        }
    };

    const faqItems = document.querySelectorAll('details');
    faqItems.forEach(item => {
        item.addEventListener('toggle', function () {
            if (this.open) {
                faqItems.forEach(otherItem => {
                    if (otherItem !== this && otherItem.open) {
                        otherItem.open = false;
                    }
                });
            }
        });
    });

    const autoScrollCarousel = function () {
        const carousel = document.querySelector('.company-carousel');
        if (!carousel) return;
        let scrollAmount = 0;
        const scrollSpeed = 1;
        const maxScroll = carousel.scrollWidth - carousel.clientWidth;
        const scroll = function () {
            scrollAmount += scrollSpeed;
            if (scrollAmount >= maxScroll) {
                scrollAmount = 0;
            }
            carousel.scrollLeft = scrollAmount;
            requestAnimationFrame(scroll);
        };
        carousel.addEventListener('mouseenter', function () {
            scrollAmount = carousel.scrollLeft;
            cancelAnimationFrame(scroll);
        });
        carousel.addEventListener('mouseleave', function () {
            requestAnimationFrame(scroll);
        });
        requestAnimationFrame(scroll);
    };

    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll();
    createParticles();
    autoScrollCarousel();

    const floatingElements = document.querySelectorAll('.card i, .company-card img');
    floatingElements.forEach(el => {
        el.classList.add('floating');
    });

    const observerOptions = {
        threshold: 0.1
    };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    }, observerOptions);
    document.querySelectorAll('.feature-cards .card, .company-card, .why-grid > div, .step, .testimony').forEach(el => {
        observer.observe(el);
    });
});
