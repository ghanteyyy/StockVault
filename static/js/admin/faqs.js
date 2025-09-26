const form = document.querySelector('.modal__content');
const add_button = document.querySelector('.btn-add');
const edit_buttons = document.querySelectorAll('.btn-edit');
const delete_buttons = document.querySelectorAll('.btn-delete');


add_button.addEventListener('click', (e) => {
    form.action = `${window.location.origin}/admin/faq/add`;
    openModal();
});


delete_buttons.forEach((delete_button) => {
    delete_button.addEventListener('click', async (e) => {
        const url = new URL('/admin/faq/delete', location.origin);
        url.searchParams.set('faq_id', delete_button.dataset.faq_id);

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


edit_buttons.forEach((button, index) => {
    button.addEventListener('click', () => {
        const question_field = document.querySelector('#question');
        const answer_field = document.querySelector('#answer');
        const faq_id_field = document.querySelector('#faq_id');

        form.action = `${window.location.origin}/admin/faq/edit`;

        faq_id_field.value = button.dataset.submit_href == 'faq/edit' ? button.dataset.faq_id : '';
        answer_field.value = button.dataset.submit_href == 'faq/edit' ? button.dataset.faq_answer : '';
        question_field.value = button.dataset.submit_href == 'faq/edit' ? button.dataset.faq_question : '';

        openModal();
    });
});


form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const question_field = document.querySelector('#question');
    const answer_field = document.querySelector('#answer');

    const error = document.querySelector('.error-message');

    if(!question_field.value || !answer_field.value){
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
        error.style.cssText = 'display: block;color:#166534;background:#dcfce7;border:1px solid #86efac;';
    }

    else{
        error.style.cssText = 'display: block;color:#b91c1c;background:#fee2e2;border:1px solid #fca5a5;';
    }

    if(form.action.split('/').slice(-2).join('/') == 'faq/add'){
        question_field.value = '';
        answer_field.value = '';
    }

    setTimeout(function() {
        $(error).fadeOut('fast');
    }, 2000);
});
