
const add_button = document.getElementById('add-btn');
add_button.innerHTML = 'Submit';

const company_prediction_form = document.getElementById('company_prediction_form');

company_prediction_form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const company_name = document.getElementById('stock-input');
    const column_type = document.getElementById('graph_options');
    const algorithm_options = document.getElementById('algorithm_options');

    const error_message = document.querySelector('.error-message');
    const company_prediction = document.querySelector('.company_prediction');

    if(!company_name.value || !column_type.value){
        error_message.style.display = 'block';
        error_message.innerHTML = 'Please complete all required fields before submitting';

        setTimeout(function() {
            $(error_message).fadeOut('fast');
        }, 2000);

        return false;
    }

    const url = new URL(`predict/company/data?company_name=${company_name.value}&column_type=${column_type}&algorithm_options=${algorithm_options.value}`, location.origin);
    url.searchParams.set('company_name', company_name.value);
    url.searchParams.set('column_type', column_type.value);

    const res = await fetch(url, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });

    const response = await res.json();
    const parsedData = JSON.parse(response.data);

    const labels = parsedData.map(item => item.date);
    const values = parsedData.map(item => item.yhat);
    const title = `${company_name.value} — ${column_type.value.toUpperCase()}`;

    updateLineChartById('predict_company_graph', title, labels, values);

    company_prediction.style.display = 'block';
});

