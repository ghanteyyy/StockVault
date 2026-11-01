(() => {
    'use strict';

    const passwordRules = {
        length: value => value.length >= 8,
        uppercase: value => /[A-Z]/.test(value),
        number: value => /[0-9]/.test(value),
        symbol: value => /[!@#$%^&*]/.test(value),
    };

    function initialize(form) {
        if(!form || form.dataset.authReady === 'true'){
            return;
        }

        form.dataset.authReady = 'true';

        const signup = form.dataset.authForm === 'signup';
        const find = selector => form.querySelector(selector);
        const field = id => find(`#${id}`);
        const submitButton = find('[data-auth-submit]');
        const submitLabel = find('[data-submit-label]');
        const refreshButton = find('[data-captcha-refresh]');
        const passwordToggle = find('[data-password-toggle]');
        const captchaInput = field('captcha-input');
        const captchaKey = find('[name="captcha_0"]');
        const captchaImage = field('captcha-image');
        const status = find('[data-auth-status]');
        const profileEmptyLabel = find('[data-profile-name]')?.textContent || 'No photo selected';
        const errorIds = {
            fullName: 'name-error',
            email: 'email-error',
            password: 'password-error',
            dob: 'dob-error',
            gender: 'gender-error',
            profilePicture: 'profile-error',
            'captcha-input': 'captcha-error',
        };

        const fieldIds = signup ? ['fullName', 'email', 'password', 'dob', 'gender', 'profilePicture', 'captcha-input'] : ['email', 'password', 'captcha-input'];

        let busy = false;
        let previewUrl = null;

        function setStatus(message) {
            if(!status){
                return;
            }

            status.textContent = message;
            status.hidden = !message;
        }

        function setBusy(nextBusy, submitting = false) {
            busy = nextBusy;
            form.setAttribute('aria-busy', String(nextBusy));
            if(submitButton){
                submitButton.disabled = nextBusy;
            }

            if(refreshButton){
                refreshButton.disabled = nextBusy;
            }

            if(submitLabel && submitButton){
                submitLabel.textContent = nextBusy && submitting ?
                    submitButton.dataset.submitLabelBusy || 'Please wait…' :
                    submitButton.dataset.submitLabelDefault || (signup ? 'Create account' : 'Sign in');
            }
        }

        function setError(id, message) {
            const input = field(id);
            const error = field(errorIds[id]);

            if(input){
                if(message){
                    input.setAttribute('aria-invalid', 'true');
                }

                else{
                    input.removeAttribute('aria-invalid');
                }
            }

            if(error){
                error.textContent = message;
                error.hidden = !message;
            }
        }

        function dateText(date) {
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
        }

        function yearsAgo(today, years) {
            const year = today.getFullYear() - years;
            const month = today.getMonth();
            const day = Math.min(today.getDate(), new Date(year, month + 1, 0).getDate());

            return new Date(year, month, day);
        }

        function dateError(value) {
            if(!/^\d{4}-\d{2}-\d{2}$/.test(value)){
                return 'Enter your date of birth.';
            }

            const [year, month, day] = value.split('-').map(Number);
            const birth = new Date(year, month - 1, day);

            if(birth.getFullYear() !== year || birth.getMonth() !== month - 1 || birth.getDate() !== day){
                return 'Enter a valid date of birth.';
            }

            const today = new Date();
            let age = today.getFullYear() - year;

            if(today.getMonth() < month - 1 || (today.getMonth() === month - 1 && today.getDate() < day)){
                age -= 1;
            }

            return age < 13 || age > 110 ? 'Your age must be between 13 and 110 years.' : '';
        }

        function profileError(file) {
            if(!file){
                return 'Choose a profile photo.';
            }

            if(!/\.(jpe?g|png)$/i.test(file.name)){
                return 'Choose a JPG or PNG image.';
            }

            if(!file.size){
                return 'Choose an image that is not empty.';
            }

            if(file.size > 5 * 1024 * 1024){
                return 'Choose an image no larger than 5 MB.';
            }

            return '';
        }

        function validationError(id) {
            const input = field(id);
            const value = input?.value || '';

            if(id === 'fullName'){
                return value.trim().length < 3 || value.trim().length > 100 ? 'Enter your full name using 3 to 100 characters.' : '';
            }

            if(id === 'email'){
                return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim()) ? '' : 'Enter a valid email address.';
            }

            if(id === 'password'){
                if(!value){
                    return 'Enter your password.';
                }

                return signup && !Object.values(passwordRules).every(rule => rule(value)) ?
                    'Use at least 8 characters, an uppercase letter, a number, and a symbol (!@#$%^&*).' : '';
            }

            if(id === 'dob'){
                return dateError(value);
            }
            if(id === 'gender'){
                return ['male', 'female', 'others'].includes(value) ? '' : 'Choose a gender from the list.';
            }
            if(id === 'profilePicture'){
                return profileError(input?.files?.[0]);
            }
            if(id === 'captcha-input'){
                return value.trim() ? '' : 'Enter the code shown above.';
            }
            return '';
        }

        function validate() {
            let firstInvalid;
            fieldIds.forEach(id => {
                const message = validationError(id);
                setError(id, message);
                if(message && !firstInvalid){
                    firstInvalid = field(id);
                }
            });
            if(firstInvalid){
                firstInvalid.focus();
            }
            return !firstInvalid;
        }

        function updatePasswordRules() {
            const value = field('password')?.value || '';
            Object.entries(passwordRules).forEach(([name, rule]) => {
                const item = find(`[data-password-rule="${name}"]`);
                if(item){
                    item.classList.toggle('is-met', rule(value));
                }
            });
        }

        function updateProfile() {
            const file = field('profilePicture')?.files?.[0];
            const name = find('[data-profile-name]');
            const preview = find('[data-profile-preview]');
            const placeholder = find('[data-profile-placeholder]');
            if(previewUrl){
                URL.revokeObjectURL(previewUrl);
            }
            previewUrl = null;
            if(preview){
                preview.hidden = true;
                preview.removeAttribute('src');
            }
            if(placeholder){
                placeholder.hidden = false;
            }
            if(name){
                name.textContent = file ? file.name : profileEmptyLabel;
            }
            if(file && !profileError(file) && preview && typeof URL.createObjectURL === 'function'){
                previewUrl = URL.createObjectURL(file);
                preview.src = previewUrl;
                preview.hidden = false;
                if(placeholder){
                    placeholder.hidden = true;
                }
            }
        }

        function useChallenge(challenge) {
            if(typeof challenge.captcha_key !== 'string' || !challenge.captcha_key ||
                typeof challenge.captcha_image_url !== 'string' || !challenge.captcha_image_url){
                return false;
            }
            captchaKey.value = challenge.captcha_key;
            captchaImage.src = challenge.captcha_image_url;
            captchaInput.value = '';
            return true;
        }

        async function requestJson(url, options) {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 15000);
            try{
                const response = await fetch(url, {
                    ...options,
                    credentials: 'same-origin',
                    signal: controller.signal
                });
                if(!response.ok){
                    throw new Error('Request failed');
                }
                const data = await response.json();
                if(!data || typeof data !== 'object'){
                    throw new Error('Unexpected response');
                }
                return data;
            }
            finally{
                clearTimeout(timeout);
            }
        }

        fieldIds.forEach(id => {
            const input = field(id);
            if(!input){
                return;
            }
            const update = () => {
                if(input.getAttribute('aria-invalid') === 'true'){
                    setError(id, validationError(id));
                }
                if(id === 'password'){
                    updatePasswordRules();
                }
            };
            input.addEventListener('input', update);
            input.addEventListener('change', update);
        });

        if(signup && field('dob')){
            const today = new Date();
            const oldest = yearsAgo(today, 111);
            oldest.setDate(oldest.getDate() + 1);
            field('dob').max = dateText(yearsAgo(today, 13));
            field('dob').min = dateText(oldest);
        }
        field('profilePicture')?.addEventListener('change', updateProfile);
        updatePasswordRules();
        if(signup){
            updateProfile();
        }

        passwordToggle?.addEventListener('click', () => {
            const password = field('password');
            if(!password){
                return;
            }
            const visible = password.type === 'password';
            password.type = visible ? 'text' : 'password';
            passwordToggle.setAttribute('aria-pressed', String(visible));
            passwordToggle.setAttribute('aria-label', visible ? 'Hide password' : 'Show password');
            const label = passwordToggle.querySelector('[data-password-label]');
            if(label){
                label.textContent = visible ? 'Hide' : 'Show';
            }
        });

        refreshButton?.addEventListener('click', async () => {
            if(busy || !captchaInput || !captchaKey || !captchaImage){
                return;
            }
            setBusy(true);
            setStatus('Loading a new code…');
            try{
                const data = await requestJson(form.dataset.captchaRefreshUrl || '/generate-captcha/', {
                    method: 'GET',
                    cache: 'no-store',
                    headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
                });
                if(!useChallenge(data)){
                    throw new Error('Missing challenge');
                }
                setError('captcha-input', '');
                setStatus('New code ready.');
                captchaInput.focus();
            }
            catch{
                setStatus('');
                setError('captcha-input', 'We couldn’t load a new code. Please try again.');
            }
            finally{
                setBusy(false);
            }
        });

        form.addEventListener('submit', async event => {
            event.preventDefault();
            if(busy){
                return;
            }
            setStatus('');
            if(!validate()){
                return;
            }
            if(!captchaInput || !captchaKey || !captchaImage){
                setStatus('The verification code is unavailable. Please reload this page.');
                return;
            }
            const answer = captchaInput.value.trim();
            const key = captchaKey.value;
            const csrf = find('[name="csrfmiddlewaretoken"]')?.value || '';
            const body = new FormData();
            body.append('captcha_0', key);
            body.append('captcha_1', answer);
            body.append('csrfmiddlewaretoken', csrf);
            let submitted = false;
            setBusy(true, true);
            setStatus('Checking the verification code…');
            try{
                const data = await requestJson(form.dataset.captchaVerifyUrl || '/verify-captcha/', {
                    method: 'POST',
                    body,
                    headers: {
                        'Accept': 'application/json',
                        'X-CSRFToken': csrf,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                });
                if(captchaInput.value.trim() !== answer || captchaKey.value !== key){
                    setStatus('The code changed. Please try again.');
                    captchaInput.focus();
                    return;
                }
                if(data.status !== true){
                    const replaced = useChallenge(data);
                    captchaInput.value = '';
                    setError('captcha-input', replaced ? 'The code didn’t match. Enter the new code.' : 'The code didn’t match. Please try again.');
                    setStatus('');
                    captchaInput.focus();
                    return;
                }
                if(!validate()){
                    setStatus('');
                    return;
                }
                setStatus(signup ? 'Creating your account…' : 'Signing you in…');
                HTMLFormElement.prototype.submit.call(form);
                submitted = true;
            }
            catch{
                setStatus('');
                setError('captcha-input', 'We couldn’t verify the code. Please try again.');
                captchaInput.focus();
            }
            finally{
                if(!submitted){
                    setBusy(false);
                }
            }
        });

        window.addEventListener('pageshow', () => {
            setBusy(false);
            if(signup){
                updateProfile();
            }
        });
        window.addEventListener('pagehide', () => {
            if(previewUrl){
                URL.revokeObjectURL(previewUrl);
            }
            previewUrl = null;
        });
    }

    window.StockVaultAuth = { initialize };
})();
