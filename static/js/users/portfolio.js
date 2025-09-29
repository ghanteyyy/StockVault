share_numberings = document.querySelectorAll('.share_numbering');

share_numberings.forEach(share_numbering => {
    share_numbering.addEventListener("input", (event)=>{
        event.target.value = event.target.value.replace(/\D/g, "");
    })
});


function validatePortfolioForm(){
    result = {"message": '', 'success': false}

    buying_rate = document.querySelector('.buying_rate').value
    number_of_stock = document.querySelector('.share_quantity').value

    if(!number_of_stock || !buying_rate){
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


window.validatePortfolioForm = validatePortfolioForm;
