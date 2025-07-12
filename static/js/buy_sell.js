const buy = document.getElementById('buy');
const sell = document.getElementById('sell');
const content = document.querySelector('.content');
const choices = document.querySelector('.choices');
const buying_selling_rate = document.querySelector('.buying_rate');

choices.addEventListener('click', (e) => {
    if(e.target.id == 'buy'){
        content.className = 'content buy-mode';
        buying_selling_rate.placeholder = 'Buying Rate';
    }

    else if(e.target.id == 'sell'){
        content.className = 'content sell-mode';
        buying_selling_rate.placeholder = 'Selling Rate';
    }
});


function validateForm() {
    const buyRadio = document.getElementById('buy');
    const sellRadio = document.getElementById('sell');
    const companyInput = document.getElementById('stock-input');
    const shareQuantity = document.querySelector('.share_quantity');
    const buyingRate = document.querySelector('.buying_rate');
    const errorMessage = document.querySelector('.error-searching-stocks');

    errorMessage.textContent = '';

    if (!buyRadio.checked && !sellRadio.checked) {
        errorMessage.textContent = 'Please select either Buy or Sell';
        return false;
    }

    if (companyInput.value.trim() === '') {
        errorMessage.textContent = 'Please enter a company name';
        companyInput.focus();
        return false;
    }

    if (shareQuantity.value.trim() === '') {
        errorMessage.textContent = 'Please enter the number of stocks';
        shareQuantity.focus();
        return false;
    }

    const quantity = parseFloat(shareQuantity.value);
    if (isNaN(quantity) || quantity <= 0) {
        errorMessage.textContent = 'Please enter a valid number of stocks';
        shareQuantity.focus();
        return false;
    }

    if (buyingRate.value.trim() === '') {
        errorMessage.textContent = 'Please enter the buying rate';
        buyingRate.focus();
        return false;
    }

    const rate = parseFloat(buyingRate.value);
    if (isNaN(rate) || rate <= 0) {
        errorMessage.textContent = 'Please enter a valid buying rate';
        buyingRate.focus();
        return false;
    }

    return true;
}
