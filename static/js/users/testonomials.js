function validateTestonomialsForm(){
    result = {"message": '', 'success': true}
    stock_name = document.querySelector('#stock-input').trim();

    if(!stock_name){
        result.success = false;
        result.message = 'Please complete all required fields before submitting'
    }

    return result

}

window.validateTestonomialsForm = validateTestonomialsForm;
