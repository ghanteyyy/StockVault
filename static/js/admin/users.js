(() => {
    'use strict';

    function initialize() {
        const today = new Date();
        const yearsAgo = years => {
            const year = today.getFullYear() - years;

            return new Date(year, today.getMonth(), Math.min(today.getDate(), new Date(year, today.getMonth() + 1, 0).getDate()));
        };

        const dateText = date => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;

        document.querySelectorAll('[data-user-dob]').forEach(input => {
            const oldest = yearsAgo(111);
            oldest.setDate(oldest.getDate() + 1);

            input.max = dateText(yearsAgo(13));
            input.min = dateText(oldest);
        });

        document.querySelectorAll('[data-user-password-toggle]').forEach(button => {
            if(button.dataset.toggleReady){
                return;
            }

            const input = document.getElementById(button.getAttribute('aria-controls'));

            if(!input){
                return;
            }

            button.dataset.toggleReady = 'true';
            const showLabel = button.getAttribute('aria-label') || 'Show password';

            button.addEventListener('click', () => {
                const visible = input.type === 'password';
                input.type = visible ? 'text' : 'password';

                button.textContent = visible ? 'Hide' : 'Show';
                button.setAttribute('aria-pressed', String(visible));
                button.setAttribute('aria-label', visible ? showLabel.replace(/^Show/, 'Hide') : showLabel);
            });
        });
    }

    if(document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', initialize, { once: true });
    }

    else{
        initialize();
    }
})();
