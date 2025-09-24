const form = document.querySelector('.modal__content');
const buttons = document.querySelectorAll('.btn-edit');
const add_button = document.querySelector('.btn-add');
const delete_buttons = document.querySelectorAll('.btn-delete');


add_button.addEventListener('click', (e) => {
    email_field = document.querySelector('.email-field');
    email_field.style.display = 'block';

    form.action = `${window.location.origin}/admin/user/add`;
    openModal();
});


delete_buttons.forEach((delete_button) => {
    delete_button.addEventListener('click', async (e) => {
        const email = e.currentTarget.dataset.email;

        const url = new URL('/admin/user/delete', location.origin);
        url.searchParams.set('email', email);

        // ajax request
        const res = await fetch(url, {
            method: 'GET',
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        });

        response = await (res.headers.get('content-type')?.includes('json') ? res.json() : res.text());

        alert(response.message);
        window.location.reload();

    });
})

buttons.forEach((button, index) => {
    button.addEventListener('click', () => {
        const email_div = document.querySelector('.email-field');

        const email_field = document.querySelector('#email');
        const name_field = document.querySelector('#name');
        const gender_field = document.querySelector('#gender');
        const dob_field = document.querySelector('#dob');
        const password_field = document.querySelector('#password');

        const { name, gender, dob, email, submit_href } = button.dataset;

        form.action = `${window.location.origin}/admin/user/edit`;

        if(submit_href == 'user/edit'){
            name_field.value = name;

            password_field_required = document.querySelector('.required.password');
            password_field_required.innerHTML = '';

            if(gender){
                gender_field.value = gender[0].toUpperCase() + gender.substring(1, gender.length).toLowerCase();
            }

            else{
                gender_field.value = '';
            }

            dob_field.value = dob;
            email_field.value = email;
        }

        else{
            email_div.style.display = 'grid';

            name_field.value = '';
            gender_field.value = '';
            dob_field.value = '';
            email_field.value = '';
            password_field.value = '';
        }
        openModal();
    });
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const email_field = document.querySelector('#email');
    const name_field = document.querySelector('#name');
    const gender_field = document.querySelector('#gender');
    const dob_field = document.querySelector('#dob');
    const password_field = document.querySelector('#password');

    const error = document.querySelector('.error-message');

    form_base_url = form.action.split('/').slice(-2).join('/');

    if((form_base_url == 'user/add' && !password_field.value) || !email_field.value || !name_field.value || !gender_field.value || !dob_field.value){
        error.style.display = 'block';
        error.innerHTML = 'Please complete all required fields before submitting';

        setTimeout(function() {
            $(error).fadeOut('fast');
        }, 2000);

        return false;
    }

    // ajax request
    const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const res = await fetch(form.action, {
        method: 'POST',
        body: new FormData(e.target),
        headers: { 'X-CSRFToken': csrf, 'X-Requested-With': 'XMLHttpRequest' }
    });

    response = await (res.headers.get('content-type')?.includes('json') ? res.json() : res.text());

    error.innerHTML = response.message;
    error.style.display = 'block'

    if(response.status){
        name_field.value = '';
        gender_field.value = '';
        dob_field.value = '';
        email_field.value = '';
        password_field.value = '';

        error.style.cssText = 'display: block;color:#166534;background:#dcfce7;border:1px solid #86efac;';
    }

    else{
        error.style.cssText = 'display: block;color:#b91c1c;background:#fee2e2;border:1px solid #fca5a5;';
    }

    setTimeout(function() {
        $(error).fadeOut('fast');
    }, 2000);

});
