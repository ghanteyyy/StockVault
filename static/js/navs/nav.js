document.addEventListener('DOMContentLoaded', function() {
    const icon_menu = document.querySelector('.iconoir-menu');
    const icon_xmark = document.querySelector('.iconoir-xmark');

    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    const overlay = document.createElement('div');

    overlay.className = 'overlay';
    document.body.appendChild(overlay);

    hamburger.addEventListener('click', function() {
        const isExpanded = this.getAttribute('aria-expanded') === 'true';
        this.setAttribute('aria-expanded', !isExpanded);

        icon_menu.classList.toggle('hide');
        icon_xmark.classList.toggle('hide');

        navLinks.classList.toggle('active');
        overlay.classList.toggle('active');

        document.body.style.overflow = isExpanded ? 'auto' : 'hidden';
    });

    overlay.addEventListener('click', function() {
        hamburger.setAttribute('aria-expanded', 'false');
        navLinks.classList.remove('active');
        this.classList.remove('active');
        document.body.style.overflow = 'auto';

        icon_menu.classList.remove('hide');
        icon_xmark.classList.add('hide');
    });

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
