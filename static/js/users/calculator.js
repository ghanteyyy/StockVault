let active = null;
submit = document.querySelector('.submit');
const wrapper = document.querySelector('.wrapper');
const choices = document.querySelectorAll('.choice');
const actionInput = document.querySelector('.action');
const input_wrapper = document.querySelector('.input-wrapper');
const buy_wrapper = document.querySelector('.buy-input-wrapper');
const sell_wrapper = document.querySelector('.sell-input-wrapper');

const charges = {
    broker: {
        minBrokerage: 10,
        slabs: [
            { upTo: 50_000, rate: 0.0036 },
            { upTo: 500_000, rate: 0.0033 },
            { upTo: 2_000_000, rate: 0.0031 },
            { upTo: 10_000_000, rate: 0.0027 },
            { upTo: Infinity, rate: 0.0024 },
        ],
    },
    sebonFeeRate: 0.00015,
    dpCharge: 25,
    capitalGainsTax: {
        "Less than a year (7.5%)": 0.075,
        "More than a year (5%)": 0.05,
        "Institutional (10%)": 0.10,
    }
};


choices.forEach(choice => {
    choice.addEventListener('click', () => {
        if (active === choice) {
            choices.forEach(c => c.style.flex = '1');
            active = null;
            actionInput.value = '';

            wrapper.style.display = 'none';
            submit.style.display = 'none';
            document.querySelector('.output-wrapper').replaceChildren();
        }
        else {
            choices.forEach(c => c.style.flex = c === choice ? '4' : '1');
            active = choice;

            actionInput.value = choice.classList.contains('buy') ? 'buy' : 'sell';

            wrapper.style.display = 'flex';
            submit.style.display = 'block';

            if(actionInput.value == 'buy'){
                sell_wrapper.style.display = 'none';
                buy_wrapper.style.display = 'flex';

                submit.classList.remove('sell-submit');
            }
            else{
                submit.classList.add('sell-submit');

                buy_wrapper.style.display = 'none';
                sell_wrapper.style.display = 'flex';
            }
        }
    });
});



submit.addEventListener("click", () => {
    if(actionInput.value == "buy"){
        buy_share();
    }

    else if(actionInput.value == "sell"){
        sell_share();
    }
});


function formatPrice(num) {
    const rounded = parseFloat(num.toFixed(2));

    return rounded.toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
}


function buy_shares_calculation(share_quantity, price_per_share){
    total_purchase_amount = share_quantity * price_per_share;

    brokerage_rate = charges.broker.slabs.find(s=>total_purchase_amount<=s.upTo).rate;
    brokerage_commission = total_purchase_amount * brokerage_rate;
    brokerage_commission = Math.max(brokerage_commission, charges.broker.minBrokerage);

    sebon_commission = total_purchase_amount * charges.sebonFeeRate;

    dp_charge = charges.dpCharge;

    total_amount = total_purchase_amount + brokerage_commission + sebon_commission + dp_charge

    return {
        'total_purchase_amount': formatPrice(total_purchase_amount),
        'bokerage_commission': formatPrice(brokerage_commission),
        'sebon_commission': formatPrice(sebon_commission),
        'dp_charge': formatPrice(dp_charge),
        'total_amount': formatPrice(total_amount)
    }
}


function sell_share_calculation(buy_type, share_quantity, purchase_value, selling_price, cgt_value){
    secondary = null;
    total_purchase_amount = share_quantity * purchase_value;

    if(buy_type == 'secondary'){
        brokerage_rate = charges.broker.slabs.find(s=>total_purchase_amount<=s.upTo).rate;
        brokerage_commission = total_purchase_amount * brokerage_rate;
        brokerage_commission = Math.max(brokerage_commission, charges.broker.minBrokerage);

        sebon_commission = total_purchase_amount * charges.sebonFeeRate;
        dp_charge = charges.dpCharge;

        total_payable_amount = total_purchase_amount + brokerage_commission + sebon_commission + dp_charge

        secondary = {
            "secondary": {
                "total_payable_amount": formatPrice(total_payable_amount),
                "total_purchased_amount": formatPrice(total_purchase_amount),
                "brokerage_commission": formatPrice(brokerage_commission),
                "sebon_commission": formatPrice(sebon_commission),
                "dp_charge": formatPrice(dp_charge)
            }
        }

        total_purchase_amount = total_payable_amount;
    }

    total_selling_amount = share_quantity * selling_price;

    brokerage_rate = charges.broker.slabs.find(s=>total_selling_amount<=s.upTo).rate;
    brokerage_commission = total_selling_amount * brokerage_rate;

    sebon_commission = total_selling_amount * charges.sebonFeeRate;
    dp_charge = charges.dpCharge;

    net_amount_before_CGT = total_selling_amount - brokerage_commission - sebon_commission - dp_charge;

    capital_gain = net_amount_before_CGT - total_purchase_amount;
    capital_gain_tax = charges.capitalGainsTax[cgt_value] * capital_gain;

    profit_amount = capital_gain - capital_gain_tax
    final_receivable_amount = net_amount_before_CGT - capital_gain_tax

    return {
        ...secondary,
        "total_purchased_amount": formatPrice(total_purchase_amount),
        "total_selling_amount": formatPrice(total_selling_amount),
        "brokerage_commission": formatPrice(brokerage_commission),
        "sebon_commission": formatPrice(sebon_commission),
        "dp_charge": formatPrice(dp_charge),
        "profit_amount": formatPrice(profit_amount),
        "capital_gain_tax": formatPrice(capital_gain_tax),
        "final_receivable_amount": formatPrice(final_receivable_amount)
    }
}


function buy_share() {
    number_regex = /^-?\d+$/;
    float_regex = /^-?\d+(\.\d+)?$/;

    const error = document.querySelector('.error-message');

    const shareQuantity = document.querySelector('#share_quantity').value;
    const sharePrice = document.querySelector('#share_price').value;

    if(!number_regex.test(shareQuantity) || !float_regex.test(sharePrice)){
        error.style.display = 'block';
        return;
    }

    else{
        error.style.display = 'none';
    }

    calculated_values = buy_shares_calculation(shareQuantity, sharePrice);
    document.querySelector('.output-wrapper').replaceChildren();

    makeOutputInnerDivs("Total Purchase Amount", calculated_values.total_purchase_amount);
    makeOutputInnerDivs(`Broker Commission (${brokerage_rate * 100}%)`, calculated_values.bokerage_commission);
    makeOutputInnerDivs(`SEBON Commission (${charges.sebonFeeRate * 100}%)`, calculated_values.sebon_commission);
    makeOutputInnerDivs("DP Charge", calculated_values.dp_charge);
    makeOutputInnerDivs("Total Payable Amount", calculated_values.total_amount, '.output-wrapper', 'answer-div');
}


function sell_share() {
    number_regex = /^-?\d+$/;
    float_regex = /^-?\d+(\.\d+)?$/;

    const error = document.getElementsByClassName('error-message')[1];

    buy_type = document.querySelector('input[name="buy_type"]:checked')?.value || null;
    share_quantity = document.querySelector('#share_quantity_sell').value;
    purchase_value = document.querySelector('#purchase_price').value;
    selling_price = document.querySelector('#selling_price').value;
    cgt_value = document.getElementById('CGT').value;

    if(!buy_type || !number_regex.test(share_quantity) || !float_regex.test(purchase_value) || !float_regex.test(selling_price || !cgt_value)){

        error.style.display = 'block';
        return;
    }

    else{
        error.style.display = 'none';
    }

    calculated_values = sell_share_calculation(buy_type, share_quantity, purchase_value, selling_price, cgt_value);

    document.querySelector('.output-wrapper').replaceChildren();

    if(buy_type == 'secondary'){
        makeOutputInnerDivs(`Total Purchased Amount`, calculated_values.secondary.total_purchased_amount);
        makeOutputInnerDivs(`Broker Commission (${brokerage_rate * 100}%)`, calculated_values.secondary.brokerage_commission);
        makeOutputInnerDivs(`SEBON Commission (${charges.sebonFeeRate * 100}%)`, calculated_values.secondary.sebon_commission);
        makeOutputInnerDivs("DP Charge", formatPrice(dp_charge));
        makeOutputInnerDivs("Total Payable Amount", calculated_values.secondary.total_payable_amount, '.output-wrapper', 'answer-div');
    }

    makeOutputInnerDivs("Total Selling Amount", calculated_values.total_selling_amount);
    makeOutputInnerDivs(`Broker Commission (${brokerage_rate * 100}%)`, calculated_values.brokerage_commission);
    makeOutputInnerDivs(`SEBON Commission (${charges.sebonFeeRate * 100}%)`, calculated_values.sebon_commission);
    makeOutputInnerDivs("DP Charge", calculated_values.dp_charge);
    makeOutputInnerDivs(`Capital Gain Tax (${charges.capitalGainsTax[cgt_value] * 100}%)`, calculated_values.capital_gain_tax);
    makeOutputInnerDivs("Final Receivable Amount", calculated_values.final_receivable_amount);
    makeOutputInnerDivs("Profit Amount", calculated_values.profit_amount, '.output-wrapper', 'answer-div');
}


function makeOutputInnerDivs(text1 = '', text2 = '', wrapperSelector = '.output-wrapper', innerClassName='') {
    const wrapper = document.querySelector(wrapperSelector);

    if (!wrapper) {
        return null;
    }

    const div = document.createElement('div');
    div.className = `output-row ${innerClassName}`;

    const p1 = document.createElement('p');
    p1.textContent = text1;

    const p2 = document.createElement('p');
    p2.textContent = text2;

    div.append(p1, p2);
    wrapper.appendChild(div);

    return div;
}
