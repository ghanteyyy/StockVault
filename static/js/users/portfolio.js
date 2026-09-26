share_numberings = document.querySelectorAll('.share_numbering');

share_numberings.forEach(share_numbering => {
    share_numbering.addEventListener("input", (event)=>{
        event.target.value = event.target.value.replace(/\D/g, "");
    })
});


function validatePortfolioForm(){
    result = {"message": '', 'success': false}

    buying_rate = document.querySelector('.buying_rate').value;
    number_of_stock = document.querySelector('.share_quantity').value;
    buy_type = document.querySelector('#buy-type').value;


    if(!number_of_stock || !buying_rate || !buy_type){
        result.message = 'Please complete all required fields before submitting'
    }

    else if(!parseInt(number_of_stock) || !parseFloat(buying_rate)){
        result.message = 'Number of stock or buying rate must be negative values'
    }

    else{
        result.success = true;
    }

    return result

}

// Delete Portfolios
const fa_trashes = document.querySelectorAll('.fa-trash');

fa_trashes.forEach((fa_trash) => {
    fa_trash.addEventListener("click", () => {
        const portfolioItem = fa_trash.closest('.portfolio-item');

        delete_portfolio(portfolioItem, fa_trash.dataset.companyId);
    });
});


function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;
            }
        }
    }

    return cookieValue;
}


async function delete_portfolio(element, company_id) {
    try {
        const response = await fetch('/portfolio/delete/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                company_id: company_id
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const data = await response.json();
        error_class_name = data.status ? "success-message" : "error-message";

        element.remove();

        const content = document.querySelector('.content');
        const errorMessage = document.createElement('p');
        errorMessage.classList.add(error_class_name);

        errorMessage.textContent = data.message;
        errorMessage.style.display = 'block';
        errorMessage.style.position = 'fixed';
        errorMessage.style.zIndex = 999999999999999;
        errorMessage.style.top = 0;

        content.prepend(errorMessage);

        remove_error_message(errorMessage);

    } catch (error) {
        console.error('Request failed:', error);
    }
}

window.validatePortfolioForm = validatePortfolioForm;
