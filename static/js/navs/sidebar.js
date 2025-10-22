document.addEventListener('DOMContentLoaded', () => {
    let hamburger_values = ['☰', '✖'];

    const hamburgerBtn = document.querySelector('#hamburger-btn');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');

    hamburgerBtn.addEventListener('click', () => {
        hamburger_values = hamburger_values.reverse();

        hamburgerBtn.classList.toggle('open');
        hamburgerBtn.innerHTML = hamburger_values[0];

        sidebar.classList.toggle('open');
        mainContent.classList.toggle('shifted');
    });

    document.addEventListener('click', (event) => {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(event.target) && !hamburgerBtn.contains(event.target)) {
                sidebar.classList.remove('open');
                mainContent.classList.remove('shifted');
            }
        }
    });
});
