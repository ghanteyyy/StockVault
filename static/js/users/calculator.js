const wrapper = document.querySelector('.wrapper');
const submit_button = document.querySelector('#submit');
const sell_submit = document.querySelector('#sell-submit');
const output = document.querySelector('#output');
const transaction_type = document.querySelector('#transaction-type');
const CGT = document.querySelector('.CGT');

const error = document.querySelector('.error-message');

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
        "365 days or less (5%)": 0.05,
        "365 days or more (3.75%)": 0.0375,
        "Institutional (10%)": 0.10,
    },
};

function formatPrice(num) {
    const rounded = parseFloat(num.toFixed(2));

    return rounded.toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
}

transaction_type.addEventListener('change', function() {
    const display = this.value === 'sell' ? 'flex' : 'none';

    selling_price_wrapper.style.display = display;
    CGT.style.display = display;

});

submit_button.addEventListener('click', function() {
    if(transaction_type.value === 'buy'){
        buy_share();
    }

    else{
        sell_share();
    }
});

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

    const sharePrice = document.querySelector('#purchase-price').value;
    const shareQuantity = document.querySelector('#share-quantity').value;
    const buy_type = document.querySelector('input[name="buy-type"]:checked')?.value || null;

    if(!number_regex.test(shareQuantity) || !float_regex.test(sharePrice || !buy_type)){
        error.style.display = 'block';
        remove_error_message(error);
        return;
    }

    else{
        error.style.display = 'none';
    }

    calculated_values = (buy_type == 'ipo') ? shareQuantity * sharePrice : buy_shares_calculation(shareQuantity, sharePrice);
    console.log(calculated_values);

    output.replaceChildren();

    if(buy_type == 'secondary'){
        makeOutputInnerDivs("Total Purchase Amount", calculated_values.total_purchase_amount);
        makeOutputInnerDivs(`Broker Commission (${brokerage_rate * 100}%)`, calculated_values.bokerage_commission);
        makeOutputInnerDivs(`SEBON Commission (${charges.sebonFeeRate * 100}%)`, calculated_values.sebon_commission);
        makeOutputInnerDivs("DP Charge", calculated_values.dp_charge);
        makeOutputInnerDivs("Total Purchased Amount", calculated_values.total_amount, innerClassName='answer-div');
    }

    else{
        makeOutputInnerDivs("Total Purchase Amount", formatPrice(calculated_values));
    }
}


function sell_share() {
    number_regex = /^-?\d+$/;
    float_regex = /^-?\d+(\.\d+)?$/;

    buy_type = document.querySelector('input[name="buy-type"]:checked')?.value || null;
    share_quantity = document.querySelector('#share-quantity').value;
    purchase_value = document.querySelector('#purchase-price').value;
    selling_price = document.querySelector('#selling-price').value;
    cgt_value = document.getElementById('CGT').value;

    if(!buy_type || !number_regex.test(share_quantity) || !float_regex.test(purchase_value) || !float_regex.test(selling_price || !cgt_value)){
        error.style.display = 'block';
        remove_error_message(error);
        return;
    }

    else{
        error.style.display = 'none';
    }

    output.replaceChildren();

    calculated_values = sell_share_calculation(buy_type, share_quantity, purchase_value, selling_price, cgt_value);
    output.replaceChildren();

    if(buy_type == 'secondary'){
        makeOutputInnerDivs(`Total Purchased Amount`, calculated_values.secondary.total_purchased_amount);
        makeOutputInnerDivs(`Broker Commission (${brokerage_rate * 100}%)`, calculated_values.secondary.brokerage_commission);
        makeOutputInnerDivs(`SEBON Commission (${charges.sebonFeeRate * 100}%)`, calculated_values.secondary.sebon_commission);
        makeOutputInnerDivs("DP Charge", formatPrice(dp_charge));
        makeOutputInnerDivs("Total Purchased Amount", calculated_values.secondary.total_payable_amount, innerClassName='answer-div');
    }

    makeOutputInnerDivs("Total Selling Amount", calculated_values.total_selling_amount);
    makeOutputInnerDivs(`Broker Commission (${brokerage_rate * 100}%)`, calculated_values.brokerage_commission);
    makeOutputInnerDivs(`SEBON Commission (${charges.sebonFeeRate * 100}%)`, calculated_values.sebon_commission);
    makeOutputInnerDivs("DP Charge", calculated_values.dp_charge);
    makeOutputInnerDivs(`Capital Gain Tax (${charges.capitalGainsTax[cgt_value] * 100}%)`, calculated_values.capital_gain_tax);
    makeOutputInnerDivs("Final Receivable Amount", calculated_values.final_receivable_amount);
    makeOutputInnerDivs("Profit Amount", calculated_values.profit_amount, innerClassName='answer-div');
}


function makeOutputInnerDivs(text1 = '', text2 = '', innerClassName='') {
    const wrapper = output;

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
