const input = document.getElementById('stock-input');
const suggestions = document.getElementById('suggestions');
const addBtn = document.getElementById('add-btn');
const inputWrapper = input.closest('.input-wrapper');
const error_searching_stocks = document.querySelector('.error-searching-stocks');

const companiesElement = document.querySelector('#companies');
const stockData = JSON.parse(companiesElement.textContent);


function validateForm(){
    input_value = input.value;

    if(!input_value || !filterSuggestions(input_value)){
        error_searching_stocks.innerHTML = 'Valid company was only expected'
        return false;
    }

    return true;
}


// Filter suggestions based on input
function filterSuggestions(query) {
    return stockData.filter(stock =>
        stock.toLowerCase().includes(query.toLowerCase())
    );
}


// Display suggestions
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


// Handle input changes
input.addEventListener('input', () => {
    const query = input.value.trim();
    if (query) {
        const filtered = filterSuggestions(query);
        showSuggestions(filtered);
    } else {
        suggestions.style.display = 'none';
    }
});


// Hide suggestions when clicking outside
document.addEventListener('click', (event) => {
    if (!inputWrapper.contains(event.target)) {
        suggestions.style.display = 'none';
    }
});
