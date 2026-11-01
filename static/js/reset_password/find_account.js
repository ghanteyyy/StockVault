(() => {
    'use strict';

    function initialize() {
        const form = document.querySelector('#password-reset-form');
        if(!form || form.dataset.recoveryReady === 'true'){
            return;
        }
        const email = form.querySelector('#email');
        const error = form.querySelector('#email-error');
        if(!email || !error){
            return;
        }
        form.dataset.recoveryReady = 'true';
        const submit = form.querySelector('[data-recovery-submit]');
        const submitLabel = form.querySelector('[data-submit-label]');
        const status = form.querySelector('[data-recovery-status]');
        let busy = false;

        function setError(message) {
            error.textContent = message;
            error.hidden = !message;
            if(message){
                email.setAttribute('aria-invalid', 'true');
            }

            else{
                email.removeAttribute('aria-invalid');
            }
        }

        function validationError() {
            const value = email.value.trim();
            if(!value || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)){
                return 'Enter a valid email address.';
            }
            return value.length > 254 ? 'Use an email address with no more than 254 characters.' : '';
        }

        function setBusy(nextBusy) {
            busy = nextBusy;
            form.setAttribute('aria-busy', String(nextBusy));
            if(submit){
                submit.disabled = nextBusy;
            }
            if(submitLabel){
                submitLabel.textContent = nextBusy ?
                    submit?.dataset.submitLabelBusy || 'Sending link…' :
                    submit?.dataset.submitLabelDefault || 'Send reset link';
            }
            if(status){
                status.textContent = nextBusy ? 'Sending your reset link…' : '';
                status.hidden = !nextBusy;
            }
        }

        if(!error.hidden && error.textContent.trim()){
            email.setAttribute('aria-invalid', 'true');
        }
        email.addEventListener('input', () => {
            if(email.getAttribute('aria-invalid') === 'true'){
                setError(validationError());
            }
        });
        form.addEventListener('submit', event => {
            if(busy){
                event.preventDefault();
                return;
            }
            const message = validationError();
            setError(message);
            if(message){
                event.preventDefault();
                email.focus();
                return;
            }
            email.value = email.value.trim();
            setBusy(true);
            // The browser submits to Django; its form owns server validation and email delivery.
        });
        window.addEventListener('pageshow', () => setBusy(false));
    }

    if(document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', initialize, { once: true });
    }

    else{
        initialize();
    }
})();
