function validateTestonomialsForm(){
    form_error = document.querySelector('.form-error-message');
    testonomial = document.querySelector('.testonomial-input').value.trim();

    if(!testonomial){
        form_error.textContent = 'Please complete all required fields before submitting';
        form_error.style.display = 'block';

        remove_error_message(form_error);

        return false;
    }

    return true;

}
