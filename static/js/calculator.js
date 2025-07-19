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
    sebonFeeRate: 0.00015,   // 0.015%
    dpCharge: 25,            // per scrip per settlement
    capitalGainsTax: {
        "Less than a year (7.5%)": 0.075,
        "More than a year (5%)": 0.05,
        "Institutional (10%)": 0.10,
    }
};


choices.forEach(choice => {
    choice.addEventListener('click', () => {
        if (active === choice) {  // Reset widths
            choices.forEach(c => c.style.flex = '1');
            active = null;
            actionInput.value = '';   // clear action

            wrapper.style.display = 'none';
            document.querySelector('.output-wrapper').replaceChildren(); // removes all children
        }

        else {  // Expand clicked, shrink others
            choices.forEach(c => c.style.flex = c === choice ? '4' : '1');
            active = choice;

            actionInput.value = choice.classList.contains('buy') ? 'buy' : 'sell';

            wrapper.style.display = 'flex';

            if(actionInput.value == 'buy'){
                sell_wrapper.style.display = 'none';
                buy_wrapper.style.display = 'flex';

                submit.classList.remove('sell-submit');
            }

            else{
                submit.classList.toggle('sell-submit');

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

    // Add commas (locale formatting)
    return rounded.toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
}


function buy_share() {
    number_regex = /^-?\d+$/;
    float_regex = /^-?\d+(\.\d+)?$/;

    const error = document.querySelector('.error');

    const shareQuantity = document.querySelector('#share_quantity').value;
    const sharePrice = document.querySelector('#share_price').value;

    if(!number_regex.test(shareQuantity) || !float_regex.test(sharePrice)){
        error.classList.add('show');
        return;
    }

    else{
        error.classList.remove('show');
    }

    total_purchase_amount = shareQuantity * sharePrice;

    // Borkerage Commission Calculation
    brokerage_rate = charges.broker.slabs.find(s=>total_purchase_amount<=s.upTo).rate;
    brokerage_commission = total_purchase_amount * brokerage_rate;
    brokerage_commission = Math.max(brokerage_commission, charges.broker.minBrokerage);    // Minimum brokerage commission is 10

    // SEBON Commission
    sebon_commission = total_purchase_amount * charges.sebonFeeRate;

    // DP Charge
    dp_charge = charges.dpCharge;

    // Total Amount
    total_amount = total_purchase_amount + brokerage_commission + sebon_commission + dp_charge

    makeOutputInnerDivs("Total Purchase Amount", formatPrice(total_purchase_amount));
    makeOutputInnerDivs(`Broker Commission (${brokerage_rate * 100}%)`, formatPrice(brokerage_commission));
    makeOutputInnerDivs(`SEBON Commission (${charges.sebonFeeRate * 100}%)`, formatPrice(sebon_commission));
    makeOutputInnerDivs("DP Charge", formatPrice(dp_charge));
    makeOutputInnerDivs("Total Payable Amount", formatPrice(total_amount));
}


function sell_share() {
    number_regex = /^-?\d+$/;
    float_regex = /^-?\d+(\.\d+)?$/;

    const error = document.querySelectorAll('.error')[1];

    buy_type = document.querySelector('input[name="buy_type"]:checked')?.value || null;
    share_quantity = document.querySelectorAll('#share_quantity')[1].value;
    purchase_value = document.querySelector('#purchase_price').value;
    selling_price = document.querySelector('#selling_price').value;
    cgt_value = document.getElementById('CGT').value;

    if(!buy_type || !number_regex.test(share_quantity) || !float_regex.test(purchase_value) || !float_regex.test(selling_price || !cgt_value)){
        error.classList.add('show');
        return;
    }

    else{
        error.classList.remove('show');
    }

    /*
        We have two cases for selling shares: IPO and Secondary.

        For IPO Example:
            Number of Shares = 24
            Purchase Price Per Share = 50
            Selling Price Per Share = 1200

            Total Purchase Amount = Number of Shares * Purchase Price Per Share
                                  = 24 * 50
                                  = 1,200

            Total Selling Amount = Number of Shares * Selling Price Per Share
                                 = 24 * 1200
                                 = 28,800

            Broker Commission = 0.36% of Total Selling Amount
                              = 0.0036 * 28,800
                              = 103.68

            SEBON Commission = 0.015% of Total Selling Amount
                             = 0.00015 * 28,800
                             = 4.32

            DP Charge = 25

            Net Amount Before CGT = Total Selling Amount - Broker Commission - SEBON Commission - DP Charge
                                  = 28,800 - 103.68 - 4.32 - 25
                                  = 28,667

            Capital Gain (Profit) = Net Amount Before CGT - Total Purchase Amount
                                  = 28,667 - 1,200
                                  = 27,467

            Capital Gain Tax (CGT) = 7.5% of Capital Gain
                                   = 0.075 * 27,467
                                   = 2,060.03

            Final Receivable Amount = Net Amount Before CGT - CGT
                                    = 28,667 - 2,060.03
                                    = 26,606.97


        For Secondary Example:
            Number of Shares = 24
            Purchase Price Per Share = 50
            Selling Price Per Share = 1200

            Total Purchase Amount = Number of Shares * Purchase Price Per Share
                                  = 24 * 50
                                  = 1,200

            Broker Commission for Purchase Amount = 0.36% * 1200
                                                  = 4.32

            SEBON Commission = 0.015% * Total Purchase Amount
                             = 0.00015 * 1,200
                             = 0.18

            DP Charge for Purchase = 25

            Total Payable Amount = Total Purchase Amount + Broker Commission for Purchase Amount + SEBON Commission + DP Charge for Purchase
                                  = 1,200 + 4.32 + 0.18 + 25
                                  = 1,229.5

            = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
            = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

            Total Selling Amount = Number of Shares * Selling Price Per Share
                                 = 24 * 1200
                                 = 28,800

            Broker Commission = 0.36% of Total Selling Amount
                              = 0.0036 * 28,800
                              = 103.68

            SEBON Commission = 0.015% of Total Selling Amount
                             = 0.00015 * 28,800
                             = 4.32

            DP Charge = 25

            Net Amount Before CGT = Total Selling Amount - Broker Commission - SEBON Commission - DP Charge
                                  = 28,800 - 103.68 - 4.32 - 25
                                  = 28,667

            Capital Gain (Profit) = Net Amount Before CGT - Total Purchase Amount
                                  = 28,667 - 1,200
                                  = 27,467

            Capital Gain Tax (CGT) = 7.5% of Capital Gain
                                   = 0.075 * 27,467
                                   = 2,060.03

            Final Receivable Amount = Net Amount Before CGT - CGT
                                    = 28,667 - 2,060.03
                                    = 26,606.97
    */

    document.querySelector('.output-wrapper').replaceChildren(); // removes all children

    total_purchase_amount = share_quantity * purchase_value;

    if(buy_type == 'secondary'){
        brokerage_rate = charges.broker.slabs.find(s=>total_purchase_amount<=s.upTo).rate;
        console.log(brokerage_rate * 100);
        brokerage_commission = total_purchase_amount * brokerage_rate;

        sebon_commission = total_purchase_amount * charges.sebonFeeRate;
        dp_charge = charges.dpCharge;

        total_payable_amount = total_purchase_amount + brokerage_commission + sebon_commission + dp_charge

        total_purchase_amount = total_payable_amount;

        makeOutputInnerDivs("Total Purchase Amount", formatPrice(total_purchase_amount));
        makeOutputInnerDivs(`Broker Commission (${brokerage_rate * 100}%)`, formatPrice(brokerage_commission));
        makeOutputInnerDivs(`SEBON Commission (${charges.sebonFeeRate * 100}%)`, formatPrice(sebon_commission));
        makeOutputInnerDivs("DP Charge", formatPrice(dp_charge), '.output-wrapper', 'separate-div');

    }

    total_selling_amount = share_quantity * selling_price;

    brokerage_rate = charges.broker.slabs.find(s=>total_selling_amount<=s.upTo).rate;
    brokerage_commission = total_selling_amount * brokerage_rate;

    sebon_commission = total_selling_amount * charges.sebonFeeRate;
    dp_charge = charges.dpCharge;

    net_amount_before_CGT = total_selling_amount - brokerage_commission - sebon_commission - dp_charge;

    capital_gain = net_amount_before_CGT - total_purchase_amount;
    capital_gain_tax = charges.capitalGainsTax[cgt_value] * capital_gain;

    final_receivable_amount = net_amount_before_CGT - capital_gain_tax

    if(buy_type == 'ipo'){
        makeOutputInnerDivs("Total Purchase Amount", formatPrice(total_purchase_amount));
    }

    makeOutputInnerDivs("Total Selling Amount", formatPrice(total_selling_amount));
    makeOutputInnerDivs(`Broker Commission (${brokerage_rate * 100}%)`, formatPrice(brokerage_commission));
    makeOutputInnerDivs(`SEBON Commission (${charges.sebonFeeRate * 100}%)`, formatPrice(sebon_commission));
    makeOutputInnerDivs("DP Charge", formatPrice(dp_charge));
    makeOutputInnerDivs("Profit Amount", formatPrice(capital_gain));
    makeOutputInnerDivs(`Capital Gain Tax (${charges.capitalGainsTax[cgt_value] * 100}%)`, formatPrice(capital_gain_tax));
    makeOutputInnerDivs("Final Receivable Amount", formatPrice(final_receivable_amount));
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
