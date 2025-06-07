document.addEventListener('DOMContentLoaded', () => {
    const hamburgerBtn = document.querySelector('#hamburger-btn');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');

    hamburgerBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        hamburgerBtn.classList.toggle('open');
        mainContent.classList.toggle('shifted');
    });

    // Close sidebar if clicked outside on mobile
    document.addEventListener('click', (event) => {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(event.target) && !hamburgerBtn.contains(event.target)) {
                sidebar.classList.remove('open');
                mainContent.classList.remove('shifted');
            }
        }
    });
});
