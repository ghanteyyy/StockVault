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
