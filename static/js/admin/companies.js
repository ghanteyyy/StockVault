(() => {
    'use strict';

    function initialize() {
        const create = document.querySelector('#company-create-dialog form');
        const edit = document.querySelector('#company-edit-dialog form');
        const remove = document.querySelector('#company-delete-dialog form');

        if(!create || !edit || !remove || create.dataset.catalogReady === 'true'){
            return;
        }

        create.dataset.catalogReady = 'true';
        document.querySelectorAll('[data-dialog-open="company-create-dialog"]').forEach(button => {
            button.addEventListener('click', () => create.reset());
        });

        document.querySelectorAll('[data-company-edit]').forEach(button => {
            button.addEventListener('click', () => {
                edit.elements.namedItem('company_id').value = button.dataset.id || '';
                edit.elements.namedItem('company_name').value = button.dataset.name || '';
                edit.elements.namedItem('company_abbreviation').value = button.dataset.symbol || '';
                edit.elements.namedItem('company_sector').value = button.dataset.sector || '';
            });
        });

        document.querySelectorAll('[data-company-delete]').forEach(button => {
            button.addEventListener('click', () => {
                remove.elements.namedItem('company_id').value = button.dataset.id || '';
                remove.querySelector('[data-delete-company-name]').textContent = button.dataset.name || 'this company';
            });
        });
    }
    if(document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', initialize, { once: true });
    }

    else{
        initialize()
    };
})();
