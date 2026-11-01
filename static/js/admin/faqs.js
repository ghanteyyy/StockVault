(() => {
    'use strict';

    function initialize() {
        const create = document.querySelector('#faq-create-dialog form');
        const edit = document.querySelector('#faq-edit-dialog form');
        const remove = document.querySelector('#faq-delete-dialog form');
        const payload = document.querySelector('#faq-records');

        if(!create || !edit || !remove || !payload || create.dataset.catalogReady === 'true'){
            return
        };

        let records;

        try{
            records = JSON.parse(payload.textContent);
        }
        catch{
            return;
        }

        create.dataset.catalogReady = 'true';

        function updateCount(form) {
            const answer = form.elements.namedItem('faq_answer');
            const count = form.querySelector('[data-character-count]');

            if(answer && count){
                count.textContent = String(answer.value.length)
            };
        }

        [create, edit].forEach(form => {
            form.elements.namedItem('faq_answer').addEventListener('input', () => updateCount(form));
            updateCount(form);
        });

        document.querySelectorAll('[data-dialog-open="faq-create-dialog"]').forEach(button => {
            button.addEventListener('click', () => {
                create.reset();
                updateCount(create);
            });
        });

        document.querySelectorAll('[data-faq-edit]').forEach(button => {
            button.addEventListener('click', () => {
                const record = records[button.dataset.id];

                if(!record){
                    return
                };

                edit.elements.namedItem('faq_id').value = button.dataset.id;
                edit.elements.namedItem('faq_question').value = record.question;
                edit.elements.namedItem('faq_answer').value = record.answer;

                updateCount(edit);
            });
        });

        document.querySelectorAll('[data-faq-delete]').forEach(button => {
            button.addEventListener('click', () => {
                const record = records[button.dataset.id];

                if(!record){
                    return
                };

                remove.elements.namedItem('faq_id').value = button.dataset.id;
                remove.querySelector('[data-delete-faq-question]').textContent = record.question || 'Untitled question';
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
