document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card');
    const search_input = document.querySelector('.search');
    const pagination = document.querySelector('.pagination');
    const error_message = document.querySelector('.error-message');

    error_message.style.display = cards.length == 0 ? 'flex' : 'none';

    if(search_input){
        search_input.addEventListener('input', (e) => {
            let is_result_available = 0;
            const query = e.target.value.trim().toLowerCase();

            if (pagination) {
                pagination.style.display = query ? 'none' : 'flex';
            }

            cards.forEach((card) => {
                let show_card = false;

                search_lists.forEach((cls) => {
                    const elements = card.querySelectorAll(`.${cls}`);

                    elements.forEach((el) => {
                        const text = (el.textContent || '').toLowerCase();

                        if (text.includes(query)) {
                            show_card = true;
                            is_result_available++;
                        }
                    });
                });

                card.style.display = show_card ? 'flex' : 'none';
            });

            error_message.style.display = is_result_available == 0 ? 'flex' : 'none';
        });
    }
});
