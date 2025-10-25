const profileImageInput = document.getElementById('profile_image');
const imagePreview = document.getElementById('image-preview');


function previewImage() {
    const file = profileImageInput.files[0];

    if (file && (file.type === 'image/png' || file.type === 'image/jpeg') && file.size <= 15 * 1024 * 1024) {
        const reader = new FileReader();
        const user_email = document.querySelector('.user_email').textContent;

        reader.onload = function (e) {
            imagePreview.src = e.target.result;
        };
        reader.readAsDataURL(file);

        const formData = new FormData();
        formData.append('profile_image', file);
        formData.append('change_profile', 'change_profile');
        formData.append('user_email', user_email);

        fetch('/admin/profile/change/profile-image', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        });

    } else {
        alert('Please select a PNG or JPEG file under 15MB.');
    }
}


function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}


function changePassword() {
    let hasErrors = false;
    const passwordError = document.getElementById('password-error');
    const user_email = document.querySelector('.user_email').textContent;
    const password_field = document.getElementById('new-password');
    const password = password_field.value.trim();

    const passwordRegex = /^(?=.*[A-Z])(?=.*[!@#$%^&*])(?=.*[0-9]).{8,}$/;

    // Validation
    if (!password || !passwordRegex.test(password)) {
        hasErrors = true;
    }

    // Display error messages
    passwordError.style.display = (password) ? 'none' : 'block';

    if (!hasErrors) {
        // Prepare FormData
        const formData = new FormData();
        formData.append('new_password', password);
        formData.append('change_password', 'change_password');
        formData.append('user_email', user_email);

        // Send POST request
        fetch('/admin/profile/change/password', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        }).then(response => {
            return response.json();
        }).then(data => {
            const success_message = document.querySelector('#success-message');
            success_message.style.display = 'flex';
            password_field.value = '';

            setTimeout(function() {
                $(success_message).fadeOut('fast');
            }, 2000);
        });
    }
}

document.querySelector('.save-button')?.addEventListener('click', changePassword);
