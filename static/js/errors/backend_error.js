close_button = document.querySelector('.close');
error_container = document.querySelector('.error-container');

if (close_button) {
    close_button.addEventListener('click', function() {
        if (error_container) {
            error_container.style.display = 'none';
        }
    });
}
