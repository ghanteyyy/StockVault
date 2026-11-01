(() => {
    'use strict';

    function initialize() {
        const form = document.querySelector('#password-reset-confirm-form');
        if(!form || form.dataset.recoveryReady === 'true'){
            return;
        }
        const password = form.querySelector('#new_password1');
        const confirmation = form.querySelector('#new_password2');
        const passwordError = form.querySelector('#new-password1-error');
        const confirmationError = form.querySelector('#new-password2-error');
        if(!password || !confirmation || !passwordError || !confirmationError){
            return;
        }
        form.dataset.recoveryReady = 'true';
        const submit = form.querySelector('[data-recovery-submit]');
        const submitLabel = form.querySelector('[data-submit-label]');
        const status = form.querySelector('[data-recovery-status]');
        const configuredMinimum = Number(form.dataset.passwordMinLength || password.minLength);
        const minimumLength = Number.isInteger(configuredMinimum) && configuredMinimum > 0 ? configuredMinimum : 8;
        let busy = false;
        let confirmationEdited = false;

        function setError(input, element, message) {
            element.textContent = message;
            element.hidden = !message;
            if(message){
                input.setAttribute('aria-invalid', 'true');
            }

            else{
                input.removeAttribute('aria-invalid');
            }
        }

        function validatePassword() {
            if(!password.value){
                return 'Enter a new password.';
            }
            return password.value.length < minimumLength ? `Use at least ${minimumLength} characters.` : '';
        }

        function validateConfirmation() {
            if(!confirmation.value){
                return 'Confirm your new password.';
            }
            return confirmation.value !== password.value ? 'The passwords do not match.' : '';
        }

        function setBusy(nextBusy) {
            busy = nextBusy;
            form.setAttribute('aria-busy', String(nextBusy));
            if(submit){
                submit.disabled = nextBusy;
            }
            if(submitLabel){
                submitLabel.textContent = nextBusy ?
                    submit?.dataset.submitLabelBusy || 'Saving password…' :
                    submit?.dataset.submitLabelDefault || 'Set new password';
            }
            if(status){
                status.textContent = nextBusy ? 'Saving your new password…' : '';
                status.hidden = !nextBusy;
            }
        }

        [
            [password, passwordError],
            [confirmation, confirmationError]
        ].forEach(([input, error]) => {
            if(!error.hidden && error.textContent.trim()){
                input.setAttribute('aria-invalid', 'true');
            }
        });
        password.addEventListener('input', () => {
            if(password.getAttribute('aria-invalid') === 'true'){
                setError(password, passwordError, validatePassword());
            }
            if(confirmation.value || confirmationEdited || confirmation.getAttribute('aria-invalid') === 'true'){
                setError(confirmation, confirmationError, validateConfirmation());
            }
        });
        confirmation.addEventListener('input', () => {
            confirmationEdited = true;
            setError(confirmation, confirmationError, validateConfirmation());
        });

        form.querySelectorAll('[data-recovery-password-toggle]').forEach(toggle => {
            const controlled = toggle.getAttribute('aria-controls');
            const input = controlled === password.id ? password : controlled === confirmation.id ? confirmation : null;
            if(!input){
                return;
            }
            const hiddenLabel = toggle.getAttribute('aria-label') || 'Show password';
            const visibleLabel = hiddenLabel.replace(/^Show\b/, 'Hide');
            toggle.addEventListener('click', () => {
                const visible = input.type === 'password';
                input.type = visible ? 'text' : 'password';
                toggle.setAttribute('aria-pressed', String(visible));
                toggle.setAttribute('aria-label', visible ? visibleLabel : hiddenLabel);
                const label = toggle.querySelector('[data-password-label]');
                if(label){
                    label.textContent = visible ? 'Hide' : 'Show';
                }
            });
        });

        form.addEventListener('submit', event => {
            if(busy){
                event.preventDefault();
                return;
            }
            const passwordMessage = validatePassword();
            const confirmationMessage = validateConfirmation();
            setError(password, passwordError, passwordMessage);
            setError(confirmation, confirmationError, confirmationMessage);
            if(passwordMessage || confirmationMessage){
                event.preventDefault();
                (passwordMessage ? password : confirmation).focus();
                return;
            }
            setBusy(true);
            // Django's SetPasswordForm validates the configured password policy on POST.
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
