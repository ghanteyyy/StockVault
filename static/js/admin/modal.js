const modal = document.getElementById('modal');
const closeBtn = document.getElementById('closeBtn');


function openModal() {
    modal.classList.remove('is-hidden');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
}


function closeModal() {
    const error = document.querySelector('.error-message');
    error.style.display = 'none';

    modal.classList.add('is-hidden');
    modal.setAttribute('aria-hidden', 'true');

    document.body.classList.remove('modal-open');

    window.location.reload();

}

closeBtn.addEventListener('click', closeModal);

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !modal.classList.contains('is-hidden')) {
        closeModal();
    }
});
