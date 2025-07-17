document.addEventListener('DOMContentLoaded', function() {
    window.toggleSidebar = function() {
        document.querySelector('.sidebar').classList.toggle('expanded');
    };
});