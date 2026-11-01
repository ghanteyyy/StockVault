(() => {
    function initializePublicNavigation() {
        const header = document.querySelector('.site-header');
        const menuToggle = document.querySelector('#site-menu-toggle');
        const menu = document.querySelector('#site-menu');

        if(header && menuToggle && menu){
            const media = typeof window.matchMedia === 'function' ?
                window.matchMedia('(max-width: 900px)') : null;
            const isMobile = () => media ? media.matches : window.innerWidth <= 900;
            let menuOpen = false;

            function setMenuOpen(nextOpen, restoreFocus = false) {
                const mobile = isMobile();
                menuOpen = Boolean(nextOpen && mobile);
                menu.classList.toggle('is-open', menuOpen);
                menuToggle.setAttribute('aria-expanded', String(menuOpen));
                menuToggle.setAttribute('aria-label', menuOpen ? 'Close navigation' : 'Open navigation');
                menu.inert = mobile && !menuOpen;
                if(mobile && !menuOpen){
                    menu.setAttribute('aria-hidden', 'true');
                }

                else{
                    menu.removeAttribute('aria-hidden');
                }
                if(restoreFocus && mobile){
                    menuToggle.focus();
                }
            }

            function synchronizeMenu() {
                const activeElement = document.activeElement;
                const focusWasInMenu = menu.contains(activeElement);
                setMenuOpen(false);
                if(isMobile() && focusWasInMenu){
                    menuToggle.focus();
                }

                else if(!isMobile() && activeElement === menuToggle){
                    menu.querySelector('a[href]')?.focus();
                }
            }

            header.classList.add('site-nav-ready');
            synchronizeMenu();
            menuToggle.addEventListener('click', () => setMenuOpen(!menuOpen));
            menu.querySelectorAll('a[href]').forEach(link => {
                link.addEventListener('click', () => setMenuOpen(false));
            });
            document.addEventListener('click', event => {
                if(menuOpen && !header.contains(event.target)){
                    setMenuOpen(false);
                }
            });
            document.addEventListener('focusin', event => {
                if(menuOpen && !header.contains(event.target)){
                    setMenuOpen(false);
                }
            });
            document.addEventListener('keydown', event => {
                if(event.key === 'Escape' && menuOpen){
                    event.preventDefault();
                    setMenuOpen(false, true);
                }
            });
            if(media?.addEventListener){
                media.addEventListener('change', synchronizeMenu);
            }

            else if(media?.addListener){
                media.addListener(synchronizeMenu);
            }

            else{
                window.addEventListener('resize', synchronizeMenu);
            }

            const updateHeader = () => header.classList.toggle('is-scrolled', (window.scrollY || 0) > 12);
            window.addEventListener('scroll', updateHeader, { passive: true });
            updateHeader();
        }
    }

    if(document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', initializePublicNavigation, { once: true });
    }

    else{
        initializePublicNavigation();
    }
})();
