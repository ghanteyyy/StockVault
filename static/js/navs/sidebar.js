(() => {
    function initializeSidebar() {
        const sidebar = document.querySelector('.sv-sidebar');
        const toggle = document.querySelector('#hamburger-btn.sv-sidebar-toggle');
        const closeButton = sidebar?.querySelector('#sidebar-close');
        const backdrop = document.querySelector('#sidebar-backdrop');
        const content = document.querySelector('#workspace-content');
        if(!sidebar || !toggle || !closeButton || !backdrop || !content){
            return;
        }

        const media = typeof window.matchMedia === 'function' ?
            window.matchMedia('(max-width: 768px)') : null;
        const isMobile = () => media ? media.matches : window.innerWidth <= 768;
        let open = false;
        let focusVersion = 0;
        const inertElements = [content, document.querySelector('.sv-mobile-nav'), document.querySelector('.sv-skip-link')].filter(Boolean);
        const previousInert = new Map();

        const initials = sidebar.querySelector('.sidebar-user-initials');
        const nameElement = sidebar.querySelector('.sidebar-user-name');

        function updateInitials(name) {
            if(!initials){
                return;
            }
            const words = name.split(/\s+/).filter(Boolean);
            initials.textContent = !words.length ? 'SV' : (words.length > 1 ?
                `${Array.from(words[0])[0]}${Array.from(words.at(-1))[0]}` :
                Array.from(words[0]).slice(0, 2).join('')).toLocaleUpperCase();
        }
        updateInitials(nameElement?.textContent.trim() || '');
        const photo = sidebar.querySelector('.sidebar-user-photo');
        if(photo){
            photo.addEventListener('error', () => {
                photo.hidden = true;
            });
            if(photo.complete && photo.getAttribute('src') && photo.naturalWidth === 0){
                photo.hidden = true;
            }
        }
        document.addEventListener('stockvault:profile-updated', event => {
            const profile = event.detail?.profile;
            if(!profile || typeof profile !== 'object'){
                return;
            }
            if(typeof profile.name === 'string'){
                if(nameElement){
                    nameElement.textContent = profile.name;
                }
                updateInitials(profile.name);
            }
            if(photo && typeof profile.image_url === 'string'){
                if(profile.image_url){
                    photo.src = profile.image_url;
                }

                else{
                    photo.removeAttribute('src');
                }
                photo.hidden = !profile.image_url;
            }
        });

        function focusableElements() {
            return [...sidebar.querySelectorAll('a[href], button, input, select, textarea, [tabindex]')]
                .filter(element => !element.disabled && !element.hidden && element.tabIndex >= 0 &&
                    element.getClientRects().length > 0);
        }

        function focusDesktopContent() {
            const activeLink = sidebar.querySelector('a[aria-current="page"]');
            (activeLink || content).focus();
        }

        function scheduleDrawerFocus(version) {
            function placeFocus(retried = false) {
                if(!open || !isMobile() || version !== focusVersion || sidebar.contains(document.activeElement)){
                    return;
                }
                const first = focusableElements()[0];
                (closeButton.getClientRects().length ? closeButton : first || closeButton).focus();
                // A visibility transition may not have resolved on the first frame.
                if(!retried && !sidebar.contains(document.activeElement) && typeof window.requestAnimationFrame === 'function'){
                    window.requestAnimationFrame(() => placeFocus(true));
                }
            }
            if(typeof window.requestAnimationFrame === 'function'){
                window.requestAnimationFrame(() => placeFocus());
            }

            else{
                placeFocus();
            }
        }

        function setState(shouldOpen, restoreFocus = true) {
            const mobile = isMobile();
            const wasOpen = open;
            open = Boolean(shouldOpen && mobile);
            const version = ++focusVersion;

            if(open){
                inertElements.forEach(element => {
                    if(!previousInert.has(element)){
                        previousInert.set(element, element.inert);
                    }
                    element.inert = true;
                });
            }

            else{
                previousInert.forEach((value, element) => {
                    element.inert = value;
                });
                previousInert.clear();
            }

            sidebar.classList.toggle('is-open', open);
            document.body.classList.toggle('sidebar-menu-open', open);
            backdrop.hidden = !open;
            toggle.setAttribute('aria-expanded', String(open));
            toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
            sidebar.inert = mobile && !open;
            if(mobile && !open){
                sidebar.setAttribute('aria-hidden', 'true');
            }

            else{
                sidebar.removeAttribute('aria-hidden');
            }

            if(wasOpen && !open){
                sidebar.dispatchEvent(new Event('stockvault:sidebar-closed'));
            }

            if(open && !wasOpen){
                scheduleDrawerFocus(version);
            }

            else if(!open && wasOpen && restoreFocus && mobile){
                toggle.focus();
            }
        }

        toggle.addEventListener('click', () => setState(!open));
        closeButton.addEventListener('click', () => setState(false));
        backdrop.addEventListener('click', () => setState(false));
        sidebar.querySelectorAll('a[href]').forEach(link => {
            link.addEventListener('click', () => {
                if(open){
                    setState(false);
                }
            });
        });

        document.addEventListener('click', event => {
            if(open && !sidebar.contains(event.target) && !toggle.contains(event.target)){
                setState(false);
            }
        });
        document.addEventListener('keydown', event => {
            if(!open){
                return;
            }
            if(event.key === 'Escape'){
                event.preventDefault();
                setState(false);
                return;
            }
            if(event.key !== 'Tab'){
                return;
            }
            const elements = focusableElements();
            if(!elements.length){
                event.preventDefault();
                closeButton.focus();
                return;
            }
            const first = elements[0];
            const last = elements.at(-1);
            const active = document.activeElement;
            if(!sidebar.contains(active) || (event.shiftKey && active === first)){
                event.preventDefault();
                (event.shiftKey ? last : first).focus();
            }

            else if(!event.shiftKey && active === last){
                event.preventDefault();
                first.focus();
            }
        });

        function synchronizeViewport() {
            const active = document.activeElement;
            setState(false, false);
            if(!isMobile() && (active === toggle || active === closeButton)){
                focusDesktopContent();
            }

            else if(isMobile() && sidebar.contains(active)){
                toggle.focus();
            }
        }
        if(media?.addEventListener){
            media.addEventListener('change', synchronizeViewport);
        }

        else if(media?.addListener){
            media.addListener(synchronizeViewport);
        }

        else{
            window.addEventListener('resize', synchronizeViewport);
        }

        setState(false, false);
    }

    if(document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', initializeSidebar, { once: true });
    }

    else{
        initializeSidebar();
    }
})();
