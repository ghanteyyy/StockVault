function validateForm(event) {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const emailError = document.getElementById('email-error');
    const passwordError = document.getElementById('password-error');

    emailError.style.display = 'none';
    passwordError.style.display = 'none';

    let hasErrors = false;

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(email)) {
        emailError.style.display = 'block';
        hasErrors = true;
    }

    if (!password) {
        passwordError.innerText = "Secret phrase is required for authentication";
        passwordError.style.display = 'block';
        hasErrors = true;
    }

    if (hasErrors) {
        event.preventDefault();
    }
}
