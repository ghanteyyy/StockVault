const modal = document.getElementById('modal');
const closeBtn = document.getElementById('closeBtn');
const overlay = modal.querySelector('.modal__overlay');


function openModal() {
    modal.classList.remove('is-hidden');
    modal.setAttribute('aria-hidden', 'false');
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');

    document.documentElement.classList.add('modal-open');
    document.body.classList.add('modal-open');
}


function closeModal() {
    const error = modal.querySelector('.error-message');
    if (error) error.style.display = 'none';

    modal.classList.add('is-hidden');
    modal.setAttribute('aria-hidden', 'true');

    document.documentElement.classList.remove('modal-open');
    document.body.classList.remove('modal-open');
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modal.classList.contains('is-hidden')) {
        closeModal();
    }
});

overlay.addEventListener('click', closeModal);
closeBtn?.addEventListener('click', closeModal);

window.openModal = openModal;
window.closeModal = closeModal;
