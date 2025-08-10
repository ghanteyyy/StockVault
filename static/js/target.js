function validateTargetForm(){
    number_regex = /^\d*\.?\d+$/;

    input_value = input.value;
    low_target = document.querySelector('.low_target').value;
    high_target = document.querySelector('.high_target').value;
    target_type = document.querySelector('#target_type').value;

    if(!input_value | !low_target | !high_targe | !target_type){
        suggestions.style.display = 'none';
        error_searching_stocks.innerHTML = 'Please complete all required fields before submitting';

        return false;
    }

    if(!number_regex.test(low_target) || !number_regex.test(high_target)){
        suggestions.style.display = 'none';
        error_searching_stocks.innerHTML = 'Please enter valid numbers for the target prices.';
        return false;
    }

    if(parseFloat(low_target) >= parseFloat(high_target)){
        suggestions.style.display = 'none';
        error_searching_stocks.innerHTML = 'Low target must be less than high target.';
        return false;
    }

    return true;
}


function validateEditTargetForm() {
    const low_target = document.getElementById('edit_low_target').value.trim();
    const high_target = document.getElementById('edit_high_target').value.trim();
    const errorMessageEl = document.querySelector('.edit-error-message');

    // Regex for numbers
    const number_regex = /^\d*\.?\d+$/;

    // Reset error
    errorMessageEl.style.display = 'none';
    errorMessageEl.textContent = '';

    if (!low_target || !high_target) {
        showError('Please complete all required fields before submitting');
        return false;
    }

    if (!number_regex.test(low_target) || !number_regex.test(high_target)) {
        showError('Please enter valid numbers for the target prices.');
        return false;
    }

    if (parseFloat(low_target) >= parseFloat(high_target)) {
        showError('Low target must be less than high target.');
        return false;
    }

    return true;

    function showError(message) {
        errorMessageEl.textContent = message;
        errorMessageEl.style.display = 'block';
    }
}


function displayEditTargetForm(target) {
    const editContainer = document.querySelector('.edit_target');
    editContainer.style.display = 'flex';

    // Stop closing modal when clicking inside the form
    editContainer.querySelector('.edit').addEventListener('click', e => e.stopPropagation());

    // Click outside closes modal
    editContainer.addEventListener('click', hideEditTargetForm);

    // Read data attributes
    const data_company_name = target.getAttribute('data-company_name');
    const data_abbreviation = target.getAttribute('data-abbreviation');
    const data_low_target = target.getAttribute('data-low_target');
    const data_high_target = target.getAttribute('data-high_target');

    // Fill modal fields
    document.querySelector('.company_title').textContent = `${data_company_name} (${data_abbreviation})`;
    document.getElementById('edit_company_abbr').value = data_abbreviation;
    document.getElementById('edit_low_target').value = data_low_target;
    document.getElementById('edit_high_target').value = data_high_target;
}

function hideEditTargetForm() {
    document.querySelector('.edit_target').style.display = 'none';
}

