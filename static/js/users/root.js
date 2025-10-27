function remove_error_message(error, timeout=2000){
    setTimeout(function() {
        $(error).fadeOut('fast');
    }, timeout);
}

window.remove_error_message = remove_error_message
