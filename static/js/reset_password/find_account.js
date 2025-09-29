function validateFindAccountForm(){
    success = true;
    console.log('HELLO CHECK CHECK');

    email_input = document.getElementsByName('email')[0];
    error_message = document.querySelector('.error-message');

    email_regex = /[a-z0-9]+@[a-z]+[.][a-z]/i;
    email_input_value = email_input.value.trim();

    if(!email_input_value || !email_regex.test(email_input_value)){
        error_message.style.display = 'block';
        error_message.innerText = 'Invalid Email';

        success = false;
    }

    return success == true;
}
