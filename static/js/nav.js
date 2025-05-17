document.addEventListener('DOMContentLoaded', function() {
        const hamburger = document.querySelector('.hamburger');
        const navLinks = document.querySelector('.nav-links');
        const overlay = document.createElement('div');
        overlay.className = 'overlay';
        document.body.appendChild(overlay);

        hamburger.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', !isExpanded);
            navLinks.classList.toggle('active');
            overlay.classList.toggle('active');

            // Toggle body scroll
            document.body.style.overflow = isExpanded ? 'auto' : 'hidden';
        });

        // Close menu when clicking on overlay
        overlay.addEventListener('click', function() {
            hamburger.setAttribute('aria-expanded', 'false');
            navLinks.classList.remove('active');
            this.classList.remove('active');
            document.body.style.overflow = 'auto';
        });

        // Close menu when clicking on a link (for single page navigation)
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    hamburger.setAttribute('aria-expanded', 'false');
                    navLinks.classList.remove('active');
                    overlay.classList.remove('active');
                    document.body.style.overflow = 'auto';
                }
            });
        });
    });
