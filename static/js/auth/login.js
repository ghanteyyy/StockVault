const form = document.getElementById('login_form');
const reload_btn = document.querySelector('.fa-rotate-right');
const captcha_image = document.getElementById('captcha-image');
const captcha_key = document.querySelector("input[name='captcha_0']");
const captcha_input = document.getElementById('captcha-input');


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


form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const emailError = document.getElementById('email-error');
    const captchaError = document.getElementById('captcha-error');
    const passwordError = document.getElementById('password-error');

    emailError.style.display = 'none';
    passwordError.style.display = 'none';

    let status = true;

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!email || !emailRegex.test(email)) {
        emailError.style.display = 'block';
        status = false;
    }

    if (!password) {
        passwordError.innerText = "Secret phrase is required for authentication";
        passwordError.style.display = 'block';
        status = false;
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
});
