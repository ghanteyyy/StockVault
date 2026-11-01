(() => {
    const calculator = document.querySelector('.sv-calculator');
    if(!calculator){
        return;
    }

    const form = calculator.querySelector('#trade-form');
    const output = calculator.querySelector('#output');
    const transactionType = calculator.querySelector('#transaction-type');
    const quantityField = calculator.querySelector('#share-quantity');
    const purchaseField = calculator.querySelector('#purchase-price');
    const sellingField = calculator.querySelector('#selling-price');
    const taxField = calculator.querySelector('#CGT');
    const error = calculator.querySelector('#calculator-error');
    const estimateState = calculator.querySelector('#estimate-state');
    const resultMode = calculator.querySelector('#result-mode');
    const resultContext = calculator.querySelector('#result-context');
    const emptyNodes = [...output.childNodes].map(node => node.cloneNode(true));
    let hasCalculated = false;

    // These mirror StockVault's configured rates in utils/calculator.py.
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
            '365 days or less (5%)': 0.05,
            '365 days or more (3.75%)': 0.0375,
            'Institutional (10%)': 0.10,
        },
    };
    const maxAmountCents = BigInt(Number.MAX_SAFE_INTEGER);
    const wholeNumber = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 });

    // Integer cents keep each component's half-up rounding consistent with Decimal.
    function applyRate(amountCents, rate) {
        const decimal = String(rate);
        const places = (decimal.split('.')[1] || '').length;
        const divisor = 10n ** BigInt(places);
        const numerator = BigInt(decimal.replace('.', ''));
        return (amountCents * numerator + divisor / 2n) / divisor;
    }

    function priceToCents(value) {
        const [whole, fraction = ''] = value.split('.');
        return BigInt(whole || '0') * 100n + BigInt(fraction.padEnd(2, '0'));
    }

    function formatMoney(cents) {
        const sign = cents < 0n ? '-' : '';
        const absolute = cents < 0n ? -cents : cents;
        return `${sign}${wholeNumber.format(absolute / 100n)}.${String(absolute % 100n).padStart(2, '0')}`;
    }

    function rateLabel(rate) {
        return `${parseFloat((rate * 100).toFixed(4))}%`;
    }

    function tradeCharges(amountCents) {
        const slab = charges.broker.slabs.find(item => item.upTo === Infinity ||
            amountCents <= BigInt(item.upTo) * 100n);
        const brokerage = applyRate(amountCents, slab.rate);
        const minimum = BigInt(charges.broker.minBrokerage) * 100n;
        return {
            rate: slab.rate,
            brokerage: brokerage < minimum ? minimum : brokerage,
            sebon: applyRate(amountCents, charges.sebonFeeRate),
            dp: BigInt(charges.dpCharge) * 100n,
        };
    }

    function calculatePurchase(quantity, priceCents, purchaseType) {
        const gross = quantity * priceCents;
        const fees = purchaseType === 'secondary' ?
            tradeCharges(gross) : {
                rate: 0,
                brokerage: 0n,
                sebon: 0n,
                dp: 0n
            };
        return {
            gross,
            fees,
            total: gross + fees.brokerage + fees.sebon + fees.dp
        };
    }

    function calculateSale(quantity, purchasePriceCents, sellingPriceCents, purchaseType, taxRate) {
        const purchase = calculatePurchase(quantity, purchasePriceCents, purchaseType);
        const gross = quantity * sellingPriceCents;
        const fees = tradeCharges(gross);
        const beforeTax = gross - fees.brokerage - fees.sebon - fees.dp;
        const gain = beforeTax - purchase.total;
        const tax = applyRate(gain > 0n ? gain : 0n, taxRate);
        const proceeds = beforeTax - tax;
        return {
            purchase,
            gross,
            fees,
            tax,
            proceeds,
            profit: proceeds - purchase.total
        };
    }

    function clearError() {
        error.hidden = true;
        error.textContent = '';
        form.querySelectorAll('[aria-invalid="true"]').forEach(field => field.removeAttribute('aria-invalid'));
    }

    function showError(field, message) {
        error.textContent = message;
        error.hidden = false;
        field.setAttribute('aria-invalid', 'true');
        field.focus();
    }

    function renderEmpty() {
        output.replaceChildren(...emptyNodes.map(node => node.cloneNode(true)));
        resultContext.textContent = '';
        estimateState.textContent = hasCalculated ? 'Update & calculate' : 'Awaiting input';
        estimateState.classList.remove('is-ready');
        estimateState.classList.toggle('is-stale', hasCalculated);
    }

    function syncMode() {
        const selected = form.querySelector('input[name="transaction-mode"]:checked');
        transactionType.value = selected?.value || 'buy';
        const selling = transactionType.value === 'sell';
        calculator.querySelector('#selling_price_wrapper').hidden = !selling;
        calculator.querySelector('.CGT').hidden = !selling;
        sellingField.required = selling;
        taxField.required = selling;
        calculator.querySelector('#purchase-price-label').textContent = selling ?
            'Original purchase price' : 'Purchase price';
        resultMode.textContent = selling ? 'Sell estimate' : 'Buy estimate';
    }

    function readPrice(field, label) {
        const value = field.value.trim();
        if(!/^(?:\d+(?:\.\d{1,2})?|\.\d{1,2})$/.test(value) ||
            !Number.isFinite(Number(value)) || Number(value) <= 0){
            showError(field, `Enter a positive ${label} with up to two decimal places.`);
            return null;
        }
        const cents = priceToCents(value);
        if(cents > maxAmountCents){
            showError(field, 'This price is too large. Please enter a smaller amount.');
            return null;
        }
        return cents;
    }

    function readTrade() {
        const quantity = quantityField.value.trim();
        if(!/^\d+$/.test(quantity) || !Number.isSafeInteger(Number(quantity)) || Number(quantity) <= 0){
            showError(quantityField, 'Enter a positive whole number of shares.');
            return null;
        }
        const quantityValue = BigInt(quantity);
        const purchaseType = form.querySelector('input[name="buy-type"]:checked');
        if(!purchaseType || !['ipo', 'secondary'].includes(purchaseType.value)){
            showError(form.querySelector('input[name="buy-type"]'), 'Choose a purchase type.');
            return null;
        }
        const purchasePrice = readPrice(purchaseField, 'purchase price');
        if(purchasePrice === null){
            return null;
        }
        const selling = transactionType.value === 'sell';
        const sellingPrice = selling ? readPrice(sellingField, 'selling price') : null;
        if(selling && sellingPrice === null){
            return null;
        }
        if(quantityValue * purchasePrice > maxAmountCents ||
            (selling && quantityValue * sellingPrice > maxAmountCents)){
            showError(quantityField, 'This trade is too large. Please reduce the quantity or price.');
            return null;
        }
        if(selling && !Object.hasOwn(charges.capitalGainsTax, taxField.value)){
            showError(taxField, 'Choose a holding period or investor type for capital gains tax.');
            return null;
        }
        return {
            quantity: quantityValue,
            purchasePrice,
            sellingPrice,
            purchaseType: purchaseType.value,
            taxRate: selling ? charges.capitalGainsTax[taxField.value] : null,
        };
    }

    function addTitle(text, parent = output) {
        const title = document.createElement('h3');
        title.className = 'output-section-title';
        title.textContent = text;
        parent.appendChild(title);
    }

    function addRow(label, amount, className = '', parent = output) {
        const row = document.createElement('div');
        row.className = `output-row ${className}`.trim();
        const name = document.createElement('p');
        name.textContent = label;
        const value = document.createElement('p');
        value.textContent = `Rs. ${formatMoney(amount)}`;
        row.append(name, value);
        parent.appendChild(row);
        return row;
    }

    function addFeeRows(fees, parent = output) {
        addRow(`Broker commission (${rateLabel(fees.rate)})`, fees.brokerage, '', parent);
        addRow(`SEBON fee (${rateLabel(charges.sebonFeeRate)})`, fees.sebon, '', parent);
        addRow('DP charge', fees.dp, '', parent);
    }

    function renderPurchase(trade, result) {
        output.replaceChildren();
        addTitle(trade.purchaseType === 'ipo' ? 'IPO purchase' : 'Purchase breakdown');
        addRow('Share value', result.gross);
        if(trade.purchaseType === 'secondary'){
            addFeeRows(result.fees);
        }

        else{
            addRow('Trade charges', 0n);
        }
        addRow('Total purchase cost', result.total, 'answer-div');
    }

    function renderSale(trade, result) {
        output.replaceChildren();
        addTitle('Sale breakdown');
        addRow('Sale value', result.gross);
        addFeeRows(result.fees);
        addRow(`Capital gains tax (${rateLabel(trade.taxRate)})`, result.tax);
        addRow('Net sale proceeds', result.proceeds, 'answer-div');
        addRow('Estimated profit / loss', result.profit,
            `profit-row ${result.profit < 0n ? 'is-negative' : 'is-positive'}`);

        if(trade.purchaseType === 'secondary'){
            const details = document.createElement('details');
            details.className = 'purchase-breakdown';
            const summary = document.createElement('summary');
            summary.textContent = 'Purchase cost breakdown';
            details.appendChild(summary);
            addRow('Original share value', result.purchase.gross, '', details);
            addFeeRows(result.purchase.fees, details);
            addRow('Total purchase cost', result.purchase.total, '', details);
            output.appendChild(details);
        }

        else{
            addRow('IPO purchase cost', result.purchase.total);
        }
    }

    form.addEventListener('submit', event => {
        event.preventDefault();
        clearError();
        const trade = readTrade();
        if(!trade){
            return;
        }
        const selling = transactionType.value === 'sell';
        const result = selling ?
            calculateSale(trade.quantity, trade.purchasePrice, trade.sellingPrice, trade.purchaseType, trade.taxRate) :
            calculatePurchase(trade.quantity, trade.purchasePrice, trade.purchaseType);
        const purchaseTotal = selling ? result.purchase.total : result.total;
        if(purchaseTotal > maxAmountCents){
            showError(quantityField, 'This trade is too large after charges. Please reduce the quantity or price.');
            return;
        }
        if(selling){
            renderSale(trade, result);
        }

        else{
            renderPurchase(trade, result);
        }
        hasCalculated = true;
        estimateState.textContent = 'Estimate ready';
        estimateState.classList.add('is-ready');
        estimateState.classList.remove('is-stale');
        resultContext.textContent = `${wholeNumber.format(trade.quantity)} ${trade.quantity === 1n ? 'share' : 'shares'} × Rs. ${formatMoney(selling ? trade.sellingPrice : trade.purchasePrice)}`;

        if(typeof matchMedia === 'function' && matchMedia('(max-width: 1180px)').matches){
            const estimateCard = calculator.querySelector('.trade-estimate-card');
            if(typeof estimateCard?.scrollIntoView === 'function'){
                estimateCard.scrollIntoView({
                    block: 'start',
                    behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
                });
            }
        }
    });

    form.addEventListener('input', () => {
        clearError();
        renderEmpty();
    });
    form.addEventListener('change', () => {
        clearError();
        syncMode();
        renderEmpty();
    });

    calculator.querySelector('#reset-calculator').addEventListener('click', () => {
        form.reset();
        hasCalculated = false;
        clearError();
        syncMode();
        renderEmpty();
        quantityField.focus();
    });

    syncMode();
})();
