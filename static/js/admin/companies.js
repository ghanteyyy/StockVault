const form = document.querySelector('.modal__content');
const buttons = document.querySelectorAll('.btn-edit');
const add_button = document.querySelector('.btn-add');
const delete_buttons = document.querySelectorAll('.btn-delete');


add_button.addEventListener('click', (e) => {
    form.action = `${window.location.origin}/admin/company/add`;
    openModal();
});


delete_buttons.forEach((delete_button) => {
    delete_button.addEventListener('click', async (e) => {
        const url = new URL('/admin/company/delete', location.origin);
        url.searchParams.set('company_id', delete_button.dataset.company_id);

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
        const company_field = document.querySelector('#company');
        const sector_field = document.querySelector('#sector');
        const company_id_field = document.querySelector('#company_id');
        const abbreviation_field = document.querySelector('#abbreviation');

        form.action = `${window.location.origin}/admin/company/edit`;

        if(button.dataset.submit_href == 'company/edit'){
            company_field.value = button.dataset.name;
            sector_field.value = button.dataset.sector;
            company_id_field.value = button.dataset.company_id
            abbreviation_field.value = button.dataset.company_abbreviation;
        }

        else{
            company_field.value = '';
            sector_field.value = '';
        }

        openModal();
    });
});


form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const company_field = document.querySelector('#company');
    const sector_field = document.querySelector('#sector');
    const abbreviation_field = document.querySelector('#abbreviation');

    const error = document.querySelector('.error-message');

    if(!company_field.value || !sector_field.value || !abbreviation_field.value){
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

    if(form.action.split('/').slice(-2).join('/') == 'company/add'){
        company_field.value = '';
        sector_field.value = '';
        abbreviation_field.value = '';
    }

    setTimeout(function() {
        $(error).fadeOut('fast');
    }, 2000);

});
