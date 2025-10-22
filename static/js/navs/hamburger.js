const sidebar = document.querySelector('.sidebar');
const hamburger = document.querySelector('.hamburger');
const iconMenu = document.querySelector('.iconoir-menu');
const iconX = document.querySelector('.iconoir-xmark');

let isOpen = false;

function render() {
    const mobile = window.innerWidth <= 900;

    if (mobile) {
        sidebar.style.width = '100%';
        sidebar.style.height = '100%';
        sidebar.style.position = 'fixed';
        sidebar.style.top = '0';
        sidebar.style.left = '0';
        sidebar.style.zIndex = '1001';
        sidebar.style.background = '#fff';
        sidebar.style.transition = 'all 0.3s ease';
        sidebar.style.display = isOpen ? 'flex' : 'none';
        sidebar.style.flexDirection = 'column';

        document.body.style.overflow = isOpen ? 'hidden' : 'auto';

        iconMenu?.classList.toggle('hide', isOpen);
        iconX?.classList.toggle('hide', !isOpen);
        hamburger.setAttribute('aria-expanded', String(isOpen));
    }

    else {
        sidebar.style.display = 'flex';
        sidebar.style.width = '';
        sidebar.style.height = '';
        sidebar.style.position = '';

        document.body.style.overflow = 'auto';

        iconX?.classList.add('hide');
        iconMenu?.classList.remove('hide');
        hamburger.setAttribute('aria-expanded', 'false');
    }
}

hamburger.addEventListener('click', (e) => {
    e.stopPropagation();
    if (window.innerWidth <= 900) {
        isOpen = !isOpen;
        render();
    }
});

document.addEventListener('click', (e) => {
    if (
        window.innerWidth <= 900 &&
        isOpen &&
        !sidebar.contains(e.target) &&
        !hamburger.contains(e.target)
    ) {
        isOpen = false;
        render();
    }
});

window.addEventListener('resize', render);
render();
