function validatePassword(){
    success = true;
    error_message = document.querySelector('.error-message');
    password1 = document.getElementsByName('new_password1')[0].value;
    password2 = document.getElementsByName('new_password2')[0].value;

    password_regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

    if(password1 != password2){
        success = false;
        error_message.style.display = 'block';
        error_message.innerText = 'Both passwords must be same';
    }

    else if(!password_regex.test(password1)){
        success = false;
        error_message.style.display = 'block';
        error_message.innerText = 'Password must be a combination of letters, numbers, and special characters, with a minimum length of 8 characters';
    }

    return success == true;
}
