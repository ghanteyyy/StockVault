const form = document.getElementById("submit-form");
const reload_btn = document.querySelector('.fa-rotate-right');
const captcha_image = document.getElementById('captcha-image');
const captcha_key = document.querySelector("input[name='captcha_0']");
const captcha_input = document.getElementById('captcha-input');

const today = new Date();
const maxDate = new Date(today.getFullYear() - 13, today.getMonth(), today.getDate());
const formattedMaxDate = maxDate.toISOString().split('T')[0];

document.getElementById('dob').max = formattedMaxDate;


function remove_error(error_element){
    setTimeout(function() {
        $(error_element).fadeOut('fast');
    }, 2000);
}


reload_btn.addEventListener('click', async (e) => {
    url = `${window.location.origin}/generate-captcha/`;
    console.log(url);

    const res = await fetch(url, {
        method: 'GET',
        headers: {'X-Requested-With': 'XMLHttpRequest'}
    });

    response = await (res.headers.get('content-type')?.includes('json') ? res.json() : res.text());

    captcha_input.value = '';
    captcha_key.value = response.captcha_key;
    captcha_image.src = response.captcha_image_url;
});


form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fullName = document.getElementById('fullName').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const dob = document.getElementById('dob').value;
    const gender = document.getElementById('gender').value;
    const profilePicture = document.getElementById('profilePicture').files;
    const nameError = document.getElementById('name-error');
    const emailError = document.getElementById('email-error');
    const passwordError = document.getElementById('password-error');
    const dobError = document.getElementById('dob-error');
    const profileError = document.getElementById('profile-error');
    const genderError = document.getElementById('gender-error');
    const captchaError = document.getElementById('captcha-error');

    nameError.style.display = 'none';
    emailError.style.display = 'none';
    passwordError.style.display = 'none';
    dobError.style.display = 'none';
    profileError.style.display = 'none';
    genderError.style.display = 'none';

    let status = true;

    if (!fullName || fullName.trim().length < 1) {
        nameError.style.display = 'block';
        status = false;;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(email)) {
        emailError.style.display = 'block';
        status = false;;
    }

    const passwordRegex = /^(?=.*[A-Z])(?=.*[!@#$%^&*])(?=.*[0-9]).{8,}$/;
    if (!password || !passwordRegex.test(password)) {
        passwordError.style.display = 'block';
        status = false;;
    }

    const dobRegex = /^\d{4}[-\/](0[1-9]|1[0-2])[-\/](0[1-9]|[12][0-9]|3[01])$/;

    if (!dob || !dobRegex.test(dob)) {
        dobError.style.display = 'block';
        status = false;;
    }

    else {
        const [year, month, day] = dob.split('-').map(Number);
        const today = new Date();
        const birthDate = new Date(year, month, day);
        const age = today.getFullYear() - birthDate.getFullYear();

        if (age > 110 || birthDate > today || isNaN(birthDate.getTime())) {
            dobError.style.display = 'block';
            status = false;;
        }
    }

    if (!gender) {
        genderError.style.display = 'block';
        status = false;;
    }

    if (!profilePicture || profilePicture.length === 0) {
        profileError.style.display = 'block';
        status = false;;
    }

    if (!captcha_input.value) {
        captchaError.innerText = "Please complete the CAPTCHA";
        captchaError.style.display = 'block';
        status = false;
    }

    if (captcha_input.value){
        url = `${window.location.origin}/verify-captcha/`;
        const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const res = await fetch(url, {
            method: 'POST',
            body: new FormData(e.target),
            headers: { 'X-CSRFToken': csrf, 'X-Requested-With': 'XMLHttpRequest' }
        });

        response = await (res.headers.get('content-type')?.includes('json') ? res.json() : res.text());

        if(!response.status){
            captcha_input.value = '';
            captcha_key.value = response.captcha_key;
            captcha_image.src = response.captcha_image_url;

            captchaError.innerText = response.message;
            captchaError.style.display = 'block';
            status = false;
        }
    }

    if(status && response.status){
        e.target.submit();
    }

    else{
        [nameError, emailError, passwordError, dobError, profileError, genderError, captchaError].forEach((error) => {
            remove_error(error);
        })
    }
});
