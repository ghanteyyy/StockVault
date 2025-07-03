const profileImageInput = document.getElementById('profile_image');
const imagePreview = document.getElementById('image-preview');


function previewImage() {
    const file = profileImageInput.files[0];

    if (file && (file.type === 'image/png' || file.type === 'image/jpeg') && file.size <= 15 * 1024 * 1024) {
        const reader = new FileReader();
        reader.onload = function (e) {
            imagePreview.src = e.target.result;
        };
        reader.readAsDataURL(file);

        const formData = new FormData();
        formData.append('profile_image', file);
        formData.append('change_profile', 'change_profile');

        fetch('/settings/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken() // For Django CSRF protection
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
    const currentPasswordError = document.getElementById('current-password-error');
    const newPasswordError = document.getElementById('new-password-error');
    const confirmPasswordError = document.getElementById('confirm-password-error');

    const currentPassword = document.getElementById('current-password').value.trim();
    const newPassword = document.getElementById('new-password').value.trim();
    const confirmPassword = document.getElementById('confirm-password').value.trim();

    const passwordRegex = /^(?=.*[A-Z])(?=.*[!@#$%^&*])(?=.*[0-9]).{8,}$/;

    // Validation
    if (!currentPassword || !passwordRegex.test(newPassword) || newPassword != confirmPassword || !newPassword && !confirmPassword) {
        hasErrors = true;
    }

    // Display error messages
    currentPasswordError.style.display = currentPassword ? 'none' : 'block';
    newPasswordError.style.display = passwordRegex.test(newPassword) ? 'none' : 'block';
    confirmPasswordError.style.display = (newPassword && confirmPassword && newPassword === confirmPassword) ? 'none' : 'block';

    if (!hasErrors) {
        // Prepare FormData
        const formData = new FormData();
        formData.append('current_password', currentPassword);
        formData.append('new_password', newPassword);
        formData.append('confirm_password', confirmPassword);
        formData.append('change_password', 'change_password');

        // Send POST request
        fetch('/settings/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCSRFToken() // For Django CSRF protection
            }
        })
        .then(response => {
            return response.json();
        }).then(data => {
            console.log('Response errors:', data.errors);
            const imagePreview = document.querySelector('#image-preview');
            if (imagePreview) {
                imagePreview.scrollIntoView({ behavior: 'smooth' });
            }

            if (data.errors) {
                console.log('Errors:', data.errors);

                // Remove existing error container if present
                const existingContainer = document.querySelector('.error-container');
                if (existingContainer) existingContainer.remove();

                // Get reference to content container
                const contentContainer = document.querySelector('.content');
                if (!contentContainer) return; // Exit if no content found

                // Create error container
                const errorContainer = document.createElement('div');
                errorContainer.className = 'error-container';

                // Create close button
                const closeButton = document.createElement('p');
                closeButton.className = 'close';
                closeButton.textContent = '✕';
                closeButton.addEventListener('click', () => errorContainer.remove());

                // Create error list
                const errorList = document.createElement('ul');
                errorList.className = 'error-list';

                // Add errors
                for (const error in data.errors) {
                    const errorItem = document.createElement('li');
                    errorItem.className = 'error-item';
                    errorItem.textContent = data.errors[error];
                    errorList.appendChild(errorItem);
                }

                // Assemble and insert before main-content
                errorContainer.appendChild(closeButton);
                errorContainer.appendChild(errorList);
                contentContainer.parentNode.insertBefore(errorContainer, contentContainer);
            }
        });
    }
}

// Attach event listener to a button or form submission
document.querySelector('.save-button')?.addEventListener('click', changePassword);
