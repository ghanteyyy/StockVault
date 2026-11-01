(() => {
    'use strict';
    const body = document.body;
    const sidebar = document.querySelector('#admin-sidebar');
    const workspace = document.querySelector('.adm-workspace');
    const menuToggle = document.querySelector('[data-admin-menu-toggle]');
    const backdrop = document.querySelector('[data-admin-menu-backdrop]');
    const media = window.matchMedia('(max-width: 900px)');
    const toast = document.querySelector('#admin-toast');

    const dialogTriggers = new WeakMap();
    let menuOpen = false;
    let toastTimer;

    function notify(message) {
        if(!toast){
            return;
        }

        clearTimeout(toastTimer);

        toast.textContent = message;
        toast.hidden = false;
        toastTimer = setTimeout(() => {
            toast.hidden = true;
        }, 6000);
    }

    function setMenu(open, restoreFocus = false) {
        if(!sidebar || !menuToggle){
            return;
        }

        menuOpen = Boolean(open && media.matches);
        body.classList.toggle('adm-menu-open', menuOpen);
        menuToggle.setAttribute('aria-expanded', String(menuOpen));
        menuToggle.setAttribute('aria-label', menuOpen ? 'Close navigation' : 'Open navigation');
        sidebar.inert = media.matches && !menuOpen;

        if(sidebar.inert){
            sidebar.setAttribute('aria-hidden', 'true');
        }

        else{
            sidebar.removeAttribute('aria-hidden');
        }

        if(workspace){
            workspace.inert = menuOpen;
        }

        if(backdrop){
            backdrop.hidden = !menuOpen;
        }

        if(menuOpen){
            const focusMenu = () => {
                if(menuOpen){
                    sidebar.querySelector('[data-admin-menu-close]')?.focus();
                }
            };

            focusMenu();
            setTimeout(focusMenu, 0);
        }

        else if(restoreFocus && media.matches){
            menuToggle.focus();
        }
    }

    menuToggle?.addEventListener('click', () => setMenu(!menuOpen, menuOpen));
    document.querySelector('[data-admin-menu-close]')?.addEventListener('click', () => setMenu(false, true));
    backdrop?.addEventListener('click', () => setMenu(false, true));

    sidebar?.addEventListener('transitionend', event => {
        if(event.target === sidebar && event.propertyName === 'transform' && menuOpen && !sidebar.contains(document.activeElement)){
            sidebar.querySelector('[data-admin-menu-close]')?.focus();
        }
    });

    media.addEventListener('change', () => {
        const focusInSidebar = sidebar?.contains(document.activeElement);
        setMenu(false, focusInSidebar);
        if(!media.matches && focusInSidebar){
            sidebar.querySelector('.adm-nav-link')?.focus();
        }
    });

    setMenu(false);

    function clearErrors(form) {
        form.querySelectorAll('[data-error-for]').forEach(error => {
            error.textContent = '';
            error.hidden = true;
        });

        form.querySelectorAll('[aria-invalid]').forEach(field => field.removeAttribute('aria-invalid'));
        const status = form.querySelector('[data-form-status]');

        if(status){
            status.textContent = '';
            status.hidden = true;
            status.classList.remove('is-error');
        }
    }

    function formStatus(form, message, error = false) {
        const status = form.querySelector('[data-form-status]');

        if(!status){
            return notify(message);
        }

        status.textContent = message;
        status.hidden = false;
        status.classList.toggle('is-error', error);
    }

    function fieldError(form, name, message) {
        const field = [...form.elements].find(item => item.name === name);
        const error = [...form.querySelectorAll('[data-error-for]')].find(item => item.dataset.errorFor === name);

        if(field){
            field.setAttribute('aria-invalid', 'true');
        }

        if(error){
            error.textContent = Array.isArray(message) ? message.join(' ') : String(message);
            error.hidden = false;
        }

        return field && field.type !== 'hidden' ? field : null;
    }

    function closeDialog(dialog) {
        if(dialog.querySelector('[data-submitting="true"]')){
            notify('Please wait for the current request to finish.');
            return;
        }

        dialog.close();
    }

    document.addEventListener('click', event => {
        const opener = event.target.closest('[data-dialog-open]');

        if(opener){
            const dialog = document.getElementById(opener.dataset.dialogOpen);

            if(dialog instanceof HTMLDialogElement && !dialog.open){
                dialog.querySelectorAll('form[data-admin-form]').forEach(clearErrors);
                dialogTriggers.set(dialog, opener);
                dialog.showModal();
                body.classList.add('adm-modal-open');
            }
        }

        const closer = event.target.closest('[data-dialog-close]');

        if(closer){
            const dialog = closer.closest('dialog');

            if(dialog){
                closeDialog(dialog);
            }
        }
    });
    document.querySelectorAll('dialog.adm-dialog').forEach(dialog => {
        dialog.addEventListener('cancel', event => {
            if(dialog.querySelector('[data-submitting="true"]')){
                event.preventDefault();
            }
        });

        dialog.addEventListener('close', () => {
            if(!document.querySelector('dialog[open]')){
                body.classList.remove('adm-modal-open');
            }
            dialogTriggers.get(dialog)?.focus();
        });

        dialog.addEventListener('click', event => {
            if(event.target !== dialog){
                return;
            }
            const rect = dialog.getBoundingClientRect();
            if(event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom){
                closeDialog(dialog);
            }
        });
    });

    document.addEventListener('keydown', event => {
        if(!menuOpen){
            return;
        }

        if(event.key === 'Escape'){
            event.preventDefault();
            setMenu(false, true);
        }

        if(event.key === 'Tab'){
            const items = [...sidebar.querySelectorAll('a[href],button:not([disabled])')].filter(item => item.getClientRects().length);
            const first = items[0],
                last = items[items.length - 1];

            if(event.shiftKey && document.activeElement === first){
                event.preventDefault();
                last?.focus();
            }

            else if(!event.shiftKey && document.activeElement === last){
                event.preventDefault();
                first?.focus();
            }
        }
    });

    document.querySelectorAll('form[data-admin-form]').forEach(form => {
        form.addEventListener('input', event => {
            const field = event.target;

            if(!field.name || field.getAttribute('aria-invalid') !== 'true' || !field.validity.valid){
                return;
            }

            field.removeAttribute('aria-invalid');
            const error = [...form.querySelectorAll('[data-error-for]')].find(item => item.dataset.errorFor === field.name);

            if(error){
                error.hidden = true;
            }
        });

        form.addEventListener('submit', async event => {
            event.preventDefault();

            if(form.dataset.submitting === 'true'){
                return;
            }

            clearErrors(form);
            let firstInvalid;

            [...form.elements].forEach(field => {
                if(field.willValidate && !field.validity.valid){
                    fieldError(form, field.name, field.validationMessage);
                    firstInvalid ||= field;
                }
            });

            if(firstInvalid){
                formStatus(form, 'Please check the highlighted fields.', true);
                firstInvalid.focus();

                return;
            }

            const csrf = form.querySelector('[name="csrfmiddlewaretoken"]')?.value;

            if(!csrf){
                return formStatus(form, 'Please refresh this page before trying again.', true);
            }

            const buttons = [...form.querySelectorAll('[type="submit"]')];
            const previous = buttons.map(button => button.disabled);

            form.dataset.submitting = 'true';
            form.setAttribute('aria-busy', 'true');

            buttons.forEach(button => {
                button.disabled = true;
            });

            formStatus(form, 'Saving your changes…');
            const controller = new AbortController();
            const timer = setTimeout(() => controller.abort(), 20000);

            try{
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form),
                    credentials: 'same-origin',
                    signal: controller.signal,
                    headers: {
                        'Accept': 'application/json',
                        'X-CSRFToken': csrf,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                });

                if(!response.headers.get('content-type')?.includes('json')){
                    throw new Error(response.status === 403 ? 'Your session or permissions changed. Refresh this page and try again.' : 'Please refresh the page and sign in again.');
                }

                const data = await response.json();

                if(!data || typeof data !== 'object' || Array.isArray(data)){
                    throw new Error('An unexpected response was received. Refresh the page and try again.');
                }

                if(!response.ok || data.status !== true){
                    let firstField;
                    Object.entries(data.errors || {}).forEach(([name, message]) => {
                        const field = fieldError(form, name, message);

                        if(!firstField){
                            firstField = field;
                        }
                    });

                    formStatus(form, data.message || 'Please check your details and try again.', true);
                    firstField?.focus();

                    return;
                }

                const message = data.message || 'Your changes have been saved.';
                formStatus(form, message);

                try{
                    sessionStorage.setItem('stockvault-admin-notice', message);
                }
                catch{
                    /* Storage can be disabled. */
                }
                form.dispatchEvent(new CustomEvent('admin:success', { bubbles: true, detail: data }));
                const destination = form.dataset.successUrl ? new URL(form.dataset.successUrl, location.href) : null;

                if(destination && destination.origin === location.origin){
                    location.assign(destination.href);
                }

                else{
                    location.reload();
                }
            }

            catch (error){
                let message = error.message || 'Could not save your changes. Please try again.';

                if(error.name === 'AbortError'){
                    message = 'The request took too long. Refresh the page to check the latest result.';
                }

                else if(error.name === 'SyntaxError'){
                    message = 'An unexpected response was received. Refresh the page and try again.';
                }

                else if(error.name === 'TypeError'){
                    message = 'Could not complete the request. Check your connection and try again.';
                }

                formStatus(form, message, true);
            }

            finally{
                clearTimeout(timer);
                delete form.dataset.submitting;
                form.setAttribute('aria-busy', 'false');

                buttons.forEach((button, index) => {
                    button.disabled = previous[index];
                });
            }
        });
    });

    try{
        const message = sessionStorage.getItem('stockvault-admin-notice');

        if(message){
            sessionStorage.removeItem('stockvault-admin-notice');
            notify(message);
        }
    }

    catch{
        /* Notices are optional when storage is disabled. */
    }
})();
