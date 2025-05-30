function validateForm(event) {
    const fullName = document.getElementById('fullName').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const dob = document.getElementById('dob').value;
    const profilePicture = document.getElementById('profilePicture').files;
    const nameError = document.getElementById('name-error');
    const emailError = document.getElementById('email-error');
    const passwordError = document.getElementById('password-error');
    const dobError = document.getElementById('dob-error');
    const profileError = document.getElementById('profile-error');
    const genderError = document.getElementById('gender-error');

    // Reset all error messages
    nameError.style.display = 'none';
    emailError.style.display = 'none';
    passwordError.style.display = 'none';
    dobError.style.display = 'none';
    profileError.style.display = 'none';
    genderError.style.display = 'none';

    let hasErrors = false;

    // Validate full name
    if (!fullName || fullName.trim().length < 1) {
        nameError.style.display = 'block';
        hasErrors = true;
    }

    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(email)) {
        emailError.style.display = 'block';
        hasErrors = true;
    }

    // Validate password
    const passwordRegex = /^(?=.*[A-Z])(?=.*[!@#$%^&*])(?=.*[0-9]).{8,}$/;
    if (!password || !passwordRegex.test(password)) {
        passwordError.style.display = 'block';
        hasErrors = true;
    }

    // Validate date of birth
    const dobRegex = /^\d{4}\/\d{2}\/\d{2}$/;
    if (!dob || !dobRegex.test(dob)) {
        dobError.style.display = 'block';
        hasErrors = true;
    } else {
        const [year, month, day] = dob.split('/').map(Number);
        const today = new Date();
        const birthDate = new Date(year, month - 1, day);
        const age = today.getFullYear() - birthDate.getFullYear();
        if (age > 110 || birthDate > today || isNaN(birthDate.getTime())) {
            dobError.style.display = 'block';
            hasErrors = true;
        }
    }

    // Validate gender
    if (!gender) {
        genderError.style.display = 'block';
        hasErrors = true;
    }

    // Validate profile picture
    if (!profilePicture || profilePicture.length === 0) {
        profileError.style.display = 'block';
        hasErrors = true;
    }

    // Prevent form submission only if there are errors
    if (hasErrors) {
        event.preventDefault();
    }
}
