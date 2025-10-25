const form = document.querySelector('.modal__content');
const add_button = document.querySelector('.btn-add');
const edit_buttons = document.querySelectorAll('.btn-edit');
const delete_buttons = document.querySelectorAll('.btn-delete');
const modal_error = document.querySelector('.modal')

add_button.addEventListener('click', (e) => {
    const question_field = document.querySelector('#question');
    const answer_field = document.querySelector('#answer');

    answer_field.value = '';
    question_field.value = '';

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

    const modal_empy_field_error = document.querySelector('.modal-error-message');
    const modal_response_message = document.querySelector('.modal-response-message');

    if(!question_field.value || !answer_field.value){
        modal_empy_field_error.style.display = 'block';

        setTimeout(function() {
            $(modal_empy_field_error).fadeOut('fast');
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

    modal_type = response.status ? 'success-message' : 'error-message';
    modal_response_message.innerHTML = response.message;
    modal_response_message.classList.add(modal_type)
    modal_response_message.style.display = 'block';

    if(form.action.split('/').slice(-2).join('/') == 'faq/add'){
        question_field.value = '';
        answer_field.value = '';
    }

    setTimeout(function() {
        $(modal_response_message).fadeOut('fast');
    }, 2000);
});
