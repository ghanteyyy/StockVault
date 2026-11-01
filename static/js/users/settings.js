(() => {
    const settings = document.querySelector('.sv-settings');
    if(!settings){
        return;
    }

    const endpoint = settings.dataset.settingsUrl || '/settings/';
    const photoForm = settings.querySelector('#photo-form');
    const detailsForm = settings.querySelector('#profile-details-form');
    const passwordForm = settings.querySelector('#password-form');
    const pending = new WeakSet();

    function hideFeedback(feedback) {
        feedback.hidden = true;
        feedback.textContent = '';
        feedback.classList.remove('is-success', 'is-error');
    }

    function showFeedback(feedback, message, success) {
        feedback.textContent = message;
        feedback.classList.toggle('is-success', success);
        feedback.classList.toggle('is-error', !success);
        feedback.hidden = false;
    }

    function clearErrors(form) {
        form.querySelectorAll('[aria-invalid="true"]').forEach(field => field.removeAttribute('aria-invalid'));
        form.querySelectorAll('.settings-field-error').forEach(message => {
            message.hidden = true;
            message.textContent = '';
        });
    }

    function fieldError(field, message, text) {
        field.setAttribute('aria-invalid', 'true');
        message.textContent = text;
        message.hidden = false;
    }

    const strings = value => (Array.isArray(value) ? value : [value])
        .filter(item => typeof item === 'string' && item.trim());

    function serverErrors(data, feedback, fields) {
        let firstInvalid = null;
        const fieldMessages = [];
        if(data.field_errors && typeof data.field_errors === 'object'){
            Object.entries(data.field_errors).forEach(([key, value]) => {
                const messages = strings(value);
                if(!messages.length){
                    return;
                }
                fieldMessages.push(...messages);
                const pair = fields[key];
                if(pair){
                    fieldError(pair[0], pair[1], messages.join(' '));
                    firstInvalid ||= pair[0];
                }
            });
        }
        const messages = strings(data.errors);
        const fallback = typeof data.message === 'string' ? data.message : '';
        showFeedback(feedback, [...new Set([...messages, ...fieldMessages])].join(' ') ||
            fallback || 'Your changes could not be saved. Please try again.', false);
        return firstInvalid;
    }

    async function saveForm(form, button, feedback, fields, onSuccess) {
        if(pending.has(form)){
            return;
        }
        const body = new FormData(form);
        const csrf = form.querySelector('[name="csrfmiddlewaretoken"]')?.value || '';
        const controls = [...form.querySelectorAll('input, select, textarea, button')];
        const originalDisabled = controls.map(control => control.disabled);
        const buttonContents = [...button.childNodes].map(node => node.cloneNode(true));
        let focusAfterSave = null;
        pending.add(form);
        controls.forEach(control => {
            control.disabled = true;
        });
        form.setAttribute('aria-busy', 'true');
        button.setAttribute('aria-busy', 'true');
        button.textContent = 'Saving…';
        hideFeedback(feedback);

        try{
            const response = await fetch(endpoint, {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'X-CSRFToken': csrf, Accept: 'application/json' },
                body,
            });
            const data = await response.json();
            if(!data || typeof data !== 'object'){
                throw new Error('Invalid response');
            }
            const hasErrors = strings(data.errors).length > 0 ||
                (data.field_errors && Object.values(data.field_errors).some(value => strings(value).length));
            if(!response.ok || data.success !== true || hasErrors){
                focusAfterSave = serverErrors(data, feedback, fields);
                return;
            }
            if(onSuccess(data) === false){
                return;
            }
            showFeedback(feedback, typeof data.message === 'string' && data.message ?
                data.message : 'Your changes have been saved.', true);
        }
        catch (error){
            showFeedback(feedback, 'Your changes could not be saved. Check your connection, then refresh the page and try again.', false);
        }
        finally{
            controls.forEach((control, index) => {
                control.disabled = originalDisabled[index];
            });
            button.replaceChildren(...buttonContents);
            button.removeAttribute('aria-busy');
            form.removeAttribute('aria-busy');
            pending.delete(form);
            if(form === detailsForm){
                updateDetailsState();
            }
            if(form === photoForm){
                updatePhotoState();
            }
            focusAfterSave?.focus();
        }
    }

    const nameField = settings.querySelector('#profile-name');
    const genderField = settings.querySelector('#profile-gender');
    const birthField = settings.querySelector('#profile-birth-date');
    const detailsButton = settings.querySelector('#save-profile');
    const detailsFeedback = settings.querySelector('#profile-feedback');
    const saveState = settings.querySelector('#profile-save-state');
    const detailErrors = {
        name: [nameField, settings.querySelector('#profile-name-error')],
        gender: [genderField, settings.querySelector('#profile-gender-error')],
        date_of_birth: [birthField, settings.querySelector('#profile-birth-date-error')],
    };
    let savedDetails = {
        name: nameField.value,
        gender: genderField.value,
        date_of_birth: birthField.value
    };

    function updateDetailsState() {
        const dirty = nameField.value !== savedDetails.name || genderField.value !== savedDetails.gender ||
            birthField.value !== savedDetails.date_of_birth;
        saveState.textContent = dirty ? 'Unsaved changes' : 'All changes saved';
        saveState.classList.toggle('is-dirty', dirty);
        detailsButton.disabled = pending.has(detailsForm) || !dirty;
    }

    function validBirthDate(value) {
        if(!value){
            return true;
        }
        if(!/^\d{4}-\d{2}-\d{2}$/.test(value) || Number(value.slice(0, 4)) < 1){
            return false;
        }
        const date = new Date(`${value}T00:00:00Z`);
        return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value &&
            (!birthField.max || value <= birthField.max);
    }

    function initials(name) {
        const words = name.trim().split(/\s+/).filter(Boolean);
        if(!words.length){
            return 'SV';
        }
        return (words.length > 1 ? `${Array.from(words[0])[0]}${Array.from(words.at(-1))[0]}` :
            Array.from(words[0]).slice(0, 2).join('')).toLocaleUpperCase();
    }

    function showSavedDetails(profile) {
        savedDetails = {
            name: typeof profile.name === 'string' ? profile.name : nameField.value.trim(),
            gender: typeof profile.gender === 'string' ? profile.gender : genderField.value,
            date_of_birth: typeof profile.date_of_birth === 'string' ? profile.date_of_birth : birthField.value,
        };
        nameField.value = savedDetails.name;
        genderField.value = savedDetails.gender;
        birthField.value = savedDetails.date_of_birth;
        const displayName = settings.querySelector('#profile-display-name');
        if(displayName){
            displayName.textContent = savedDetails.name;
        }
        settings.querySelectorAll('[data-profile-name]').forEach(element => {
            element.textContent = savedDetails.name;
        });
        const profileInitials = settings.querySelector('#profile-initials');
        if(profileInitials){
            profileInitials.textContent = initials(savedDetails.name);
        }
    }

    detailsForm.addEventListener('input', () => {
        clearErrors(detailsForm);
        hideFeedback(detailsFeedback);
        updateDetailsState();
    });
    detailsForm.addEventListener('change', () => {
        clearErrors(detailsForm);
        hideFeedback(detailsFeedback);
        updateDetailsState();
    });
    settings.querySelector('#reset-profile-details').addEventListener('click', () => {
        if(pending.has(detailsForm)){
            return;
        }
        nameField.value = savedDetails.name;
        genderField.value = savedDetails.gender;
        birthField.value = savedDetails.date_of_birth;
        clearErrors(detailsForm);
        hideFeedback(detailsFeedback);
        updateDetailsState();
    });
    detailsForm.addEventListener('submit', event => {
        event.preventDefault();
        if(pending.has(detailsForm)){
            return;
        }
        clearErrors(detailsForm);
        hideFeedback(detailsFeedback);
        const name = nameField.value.trim();
        if(!name || Array.from(name).length > 100){
            fieldError(...detailErrors.name, 'Enter your full name using up to 100 characters.');
            nameField.focus();
            return;
        }
        if(!['male', 'female', 'others'].includes(genderField.value)){
            fieldError(...detailErrors.gender, 'Choose a gender from the list.');
            genderField.focus();
            return;
        }
        if(birthField.validity?.badInput || !validBirthDate(birthField.value)){
            fieldError(...detailErrors.date_of_birth, 'Enter a valid date of birth that is not in the future.');
            birthField.focus();
            return;
        }
        nameField.value = name;
        saveForm(detailsForm, detailsButton, detailsFeedback, detailErrors, data => {
            showSavedDetails(data.profile || {});
            document.dispatchEvent(new CustomEvent('stockvault:profile-updated', {
                detail: {
                    profile: {
                        name: savedDetails.name
                    }
                },
            }));
        });
    });
    showSavedDetails(savedDetails);
    updateDetailsState();

    const photoInput = settings.querySelector('#profile_image');
    const image = settings.querySelector('#image-preview');
    const placeholder = settings.querySelector('#photo-placeholder');
    const photoName = settings.querySelector('#photo-file-name');
    const photoButton = settings.querySelector('#save-photo');
    const photoCancel = settings.querySelector('#cancel-photo');
    const photoFeedback = settings.querySelector('#photo-feedback');
    let persistedImage = image.getAttribute('src') || '';
    let stagedPhoto = null;
    let previewUrl = null;

    function releasePreview() {
        if(previewUrl){
            URL.revokeObjectURL(previewUrl);
        }
        previewUrl = null;
    }

    function displayImage(source) {
        if(source){
            image.src = source;
        }

        else{
            image.removeAttribute('src');
        }
        image.hidden = !source;
        placeholder.hidden = Boolean(source);
    }

    function updatePhotoState() {
        photoButton.disabled = pending.has(photoForm) || !stagedPhoto;
        photoCancel.hidden = !stagedPhoto;
        photoName.textContent = stagedPhoto ? stagedPhoto.name : '';
    }

    function discardPhoto() {
        stagedPhoto = null;
        photoInput.value = '';
        releasePreview();
        displayImage(persistedImage);
        updatePhotoState();
    }

    settings.querySelector('#choose-photo').addEventListener('click', () => photoInput.click());
    photoCancel.addEventListener('click', () => {
        if(pending.has(photoForm)){
            return;
        }
        discardPhoto();
        hideFeedback(photoFeedback);
    });
    photoInput.addEventListener('change', () => {
        if(pending.has(photoForm)){
            return;
        }
        hideFeedback(photoFeedback);
        const file = photoInput.files?.[0];
        if(!file){
            discardPhoto();
            return;
        }
        if(!['image/png', 'image/jpeg'].includes(file.type) || !/\.(?:png|jpe?g)$/i.test(file.name) ||
            file.size > 5 * 1024 * 1024 || file.size === 0){
            discardPhoto();
            showFeedback(photoFeedback, 'Choose a JPG or PNG photo up to 5 MB.', false);
            return;
        }
        releasePreview();
        stagedPhoto = file;
        previewUrl = URL.createObjectURL(file);
        displayImage(previewUrl);
        updatePhotoState();
    });
    image.addEventListener('error', () => {
        image.hidden = true;
        placeholder.hidden = false;
        if(stagedPhoto && image.getAttribute('src') === previewUrl){
            discardPhoto();
            showFeedback(photoFeedback, 'This photo could not be previewed. Choose a valid JPG or PNG image.', false);
        }
    });
    photoForm.addEventListener('submit', event => {
        event.preventDefault();
        if(pending.has(photoForm)){
            return;
        }
        if(!stagedPhoto){
            showFeedback(photoFeedback, 'Choose a new photo before saving.', false);
            return;
        }
        saveForm(photoForm, photoButton, photoFeedback, {}, data => {
            const source = data.profile?.image_url;
            if(typeof source !== 'string' || !source){
                showFeedback(photoFeedback, 'The updated photo was not returned. Please refresh the page and try again.', false);
                return false;
            }
            persistedImage = source;
            discardPhoto();
            document.dispatchEvent(new CustomEvent('stockvault:profile-updated', {
                detail: {
                    profile: { image_url: source }
                },
            }));
        });
    });
    window.addEventListener('pagehide', releasePreview);
    updatePhotoState();

    const currentPassword = settings.querySelector('#current-password');
    const newPassword = settings.querySelector('#new-password');
    const confirmPassword = settings.querySelector('#confirm-password');
    const passwordButton = settings.querySelector('#save-password');
    const passwordFeedback = settings.querySelector('#password-feedback');
    const passwordErrors = {
        current_password: [currentPassword, settings.querySelector('#current-password-error')],
        new_password: [newPassword, settings.querySelector('#new-password-error')],
        confirm_password: [confirmPassword, settings.querySelector('#confirm-password-error')],
    };
    const passwordLabels = {
        'current-password': 'current password',
        'new-password': 'new password',
        'confirm-password': 'confirmation password',
    };

    function passwordRules(value) {
        return {
            length: Array.from(value).length >= 8,
            upper: /[A-Z]/.test(value),
            number: /[0-9]/.test(value),
            symbol: /[!@#$%^&*]/.test(value)
        };
    }

    function updatePasswordRules() {
        const rules = passwordRules(newPassword.value);
        settings.querySelectorAll('[data-password-rule]').forEach(item => {
            item.classList.toggle('is-met', Boolean(rules[item.dataset.passwordRule]));
        });
    }

    function setPasswordVisible(button, visible) {
        const field = settings.querySelector(`#${button.dataset.togglePassword}`);
        field.type = visible ? 'text' : 'password';
        button.setAttribute('aria-pressed', String(visible));
        button.setAttribute('aria-label', `${visible ? 'Hide' : 'Show'} ${passwordLabels[field.id]}`);
        button.classList.toggle('is-visible', visible);
        const label = button.querySelector('.password-toggle-label');
        if(label){
            label.textContent = visible ? 'Hide' : 'Show';
        }
    }

    settings.querySelectorAll('[data-toggle-password]').forEach(button => button.addEventListener('click', () => {
        const field = settings.querySelector(`#${button.dataset.togglePassword}`);
        setPasswordVisible(button, field.type === 'password');
    }));
    passwordForm.addEventListener('input', () => {
        clearErrors(passwordForm);
        hideFeedback(passwordFeedback);
        updatePasswordRules();
    });
    passwordForm.addEventListener('submit', event => {
        event.preventDefault();
        if(pending.has(passwordForm)){
            return;
        }
        clearErrors(passwordForm);
        hideFeedback(passwordFeedback);
        let firstInvalid = null;
        if(!currentPassword.value){
            fieldError(...passwordErrors.current_password, 'Enter your current password.');
            firstInvalid = currentPassword;
        }
        if(!Object.values(passwordRules(newPassword.value)).every(Boolean)){
            fieldError(...passwordErrors.new_password, 'Use at least 8 characters, an uppercase letter, a number, and a symbol: ! @ # $ % ^ & *.');
            firstInvalid ||= newPassword;
        }
        if(!confirmPassword.value || newPassword.value !== confirmPassword.value){
            fieldError(...passwordErrors.confirm_password, 'Enter the same new password in both fields.');
            firstInvalid ||= confirmPassword;
        }
        if(firstInvalid){
            firstInvalid.focus();
            return;
        }
        saveForm(passwordForm, passwordButton, passwordFeedback, passwordErrors, () => {
            passwordForm.reset();
            settings.querySelectorAll('[data-toggle-password]').forEach(button => setPasswordVisible(button, false));
            updatePasswordRules();
        });
    });
    updatePasswordRules();
})();
