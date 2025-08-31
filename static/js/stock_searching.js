const input = document.getElementById('stock-input');
const suggestions = document.getElementById('suggestions');
const addBtn = document.getElementById('add-btn');
const inputWrapper = input.closest('.input-wrapper');
const error_searching_stocks = document.querySelector('.error-searching-stocks');

const companiesElement = document.querySelector('#companies');
const stockData = JSON.parse(companiesElement.textContent);


function validateStockSearchingForm(){
    input_value = input.value;

    if(!input_value){
        suggestions.style.display = 'none';
        error_searching_stocks.innerHTML = 'Please complete all required fields before submitting';
        return false;
    }

    else if(!checkValidCompany(input_value).length){
        suggestions.style.display = 'none';
        error_searching_stocks.innerHTML = 'The selected category is not recognized. It may have been removed or is no longer available. Please choose from the current list.'
        return false;
    }

    return true;
}


function checkValidCompany(query){
    return stockData.filter(stock =>
        stock.toLowerCase() == query.toLowerCase()
    );
}


function filterSuggestions(query) {
    return stockData.filter(stock =>
        stock.toLowerCase().includes(query.toLowerCase())
    );
}


function showSuggestions(suggestionList) {
    suggestions.innerHTML = '';
    const wrapperRect = inputWrapper.getBoundingClientRect();

    if (suggestionList.length > 0) {
        suggestionList.forEach(stock => {
            const div = document.createElement('div');

            div.className = 'suggestion-item';
            div.textContent = stock;

            div.addEventListener('click', () => {
                input.value = stock;
                suggestions.style.display = 'none';
            });

            suggestions.appendChild(div);
        });

        error_searching_stocks.innerHTML = ''
        suggestions.style.display = 'block';

    } else {
        suggestions.style.display = 'none';
    }
}


input.addEventListener('input', () => {
    const query = input.value.trim();
    if (query) {
        const filtered = filterSuggestions(query);
        showSuggestions(filtered);
    } else {
        suggestions.style.display = 'none';
    }
});


document.addEventListener('click', (event) => {
    if (!inputWrapper.contains(event.target)) {
        suggestions.style.display = 'none';
    }
});


window.validateStockSearchingForm = validateStockSearchingForm;
