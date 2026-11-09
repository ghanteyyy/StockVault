(() => {
    const page = document.querySelector('[data-trading-page]');
    if(!page){
        return;
    }

    const form = page.querySelector('#dealing-form');
    const tradeCompany = form.querySelector('#dealing-company');
    const bonusCompany = form.querySelector('#dealing-bonus-company');
    const quantity = form.querySelector('#dealing-quantity');
    const price = form.querySelector('#dealing-price');
    const tax = form.querySelector('#dealing-tax');
    const submit = form.querySelector('#dealing-submit');
    const submitLabel = form.querySelector('#dealing-submit-label');
    const empty = page.querySelector('#dealing-position-empty');
    const details = page.querySelector('#dealing-position-details');
    const status = page.querySelector('#dealing-quote-status');
    const holdings = JSON.parse(page.querySelector('#dealing-holdings-data').textContent);
    const money = new Intl.NumberFormat('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const whole = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 });
    let timer;
    let activeRequest;
    let quoteVersion = 0;
    let company = mode() === 'bonus' ? bonusCompany : tradeCompany;

    form.noValidate = false;

    function mode() {
        return form.querySelector('[name="transaction_type"]:checked')?.value || 'buy';
    }

    function formatMoney(value) {
        if(value === null || value === undefined || !Number.isFinite(Number(value))){
            return '—';
        }
        return money.format(value);
    }

    function showHolding(holding) {
        empty.hidden = Boolean(holding);
        details.hidden = !holding;
        if(!holding){
            page.querySelector('#dealing-empty-description').textContent = company.value ?
                'You do not hold shares in this company yet. Record a purchase to start your position.' :
                'Choose a company to see your shares, average cost, and break-even selling price.';
            return;
        }

        page.querySelector('#position-company-name').textContent = company.selectedOptions[0].textContent;
        page.querySelector('#position-quantity').textContent = whole.format(Number(holding.quantity));
        page.querySelector('#position-cost').textContent = formatMoney(holding.total_cost);
        page.querySelector('#position-average').textContent = formatMoney(holding.average_cost);
        page.querySelector('#position-break-even').textContent = formatMoney(holding.break_even_price);
        const soldQuantity = holding.sell_quantity || holding.quantity;
        page.querySelector('#position-break-even-context').textContent =
            `Estimated price to recover your purchase cost for ${whole.format(Number(soldQuantity))} shares after selling charges.`;
    }

    async function updateQuote(version) {
        activeRequest = new AbortController();
        const url = new URL(form.action, window.location.href);
        url.searchParams.set('quote', '1');
        url.searchParams.set('company', company.value);
        url.searchParams.set('transaction_type', mode());
        url.searchParams.set('cgt_type', tax.value);
        if(mode() === 'sell' && quantity.value){
            url.searchParams.set('quantity', quantity.value);
        }

        details.setAttribute('aria-busy', 'true');
        try {
            const response = await fetch(url, {
                credentials: 'same-origin',
                headers: { Accept: 'application/json' },
                signal: activeRequest.signal
            });
            const data = await response.json();
            if(version !== quoteVersion){
                return;
            }
            if(!response.ok){
                page.querySelector('#position-break-even').textContent = '—';
                page.querySelector('#position-break-even-context').textContent = 'Check the sale details to calculate the break-even price.';
                status.textContent = data.errors?.join(' ') || 'Check the share quantity and tax category.';
                status.classList.add('is-error');
                return;
            }
            showHolding(data.holding);
            status.textContent = '';
            status.classList.remove('is-error');
        }
        catch(error) {
            if(error.name !== 'AbortError' && version === quoteVersion){
                page.querySelector('#position-break-even').textContent = '—';
                page.querySelector('#position-break-even-context').textContent = 'The latest estimate is unavailable.';
                status.textContent = 'Unable to refresh the break-even price. Reload the page to try again.';
                status.classList.add('is-error');
            }
        }
        finally {
            if(version === quoteVersion){
                activeRequest = null;
                details.removeAttribute('aria-busy');
            }
        }
    }

    function scheduleQuote(immediate = false) {
        window.clearTimeout(timer);
        if(activeRequest){
            activeRequest.abort();
        }
        quoteVersion += 1;
        status.textContent = '';
        status.classList.remove('is-error');
        if(!company.value){
            details.removeAttribute('aria-busy');
            showHolding(null);
            return;
        }
        const version = quoteVersion;
        timer = window.setTimeout(() => updateQuote(version), immediate ? 0 : 350);
    }

    function syncMode() {
        const selected = mode();
        const previousCompany = company;
        company = selected === 'bonus' ? bonusCompany : tradeCompany;
        if(company !== previousCompany){
            const previousValue = previousCompany.value;
            company.value = Array.from(company.options).some(option => option.value === previousValue) ? previousValue : '';
        }
        tradeCompany.disabled = selected === 'bonus';
        bonusCompany.disabled = selected !== 'bonus';
        submit.disabled = selected === 'bonus' && bonusCompany.options.length === 1;
        price.required = selected !== 'bonus';
        price.disabled = selected === 'bonus';
        page.querySelector('#dealing-price-label').textContent = selected === 'sell' ?
            'Selling price per share' : 'Purchase price per share';
        if(selected === 'sell'){
            submitLabel.textContent = 'Record sale';
        }

        else if(selected === 'bonus'){
            submitLabel.textContent = 'Add bonus shares';
        }

        else{
            submitLabel.textContent = 'Record purchase';
        }
        showHolding(holdings[company.value] || null);
        scheduleQuote(true);
    }

    form.querySelectorAll('[name="transaction_type"]').forEach(input => {
        input.addEventListener('change', syncMode);
    });
    [tradeCompany, bonusCompany].forEach(picker => {
        picker.addEventListener('change', () => {
            showHolding(holdings[company.value] || null);
            scheduleQuote(true);
        });
    });
    quantity.addEventListener('input', () => {
        if(mode() === 'sell'){
            scheduleQuote();
        }
    });
    tax.addEventListener('change', () => {
        scheduleQuote(true);
    });
    page.querySelectorAll('[data-pick-company]').forEach(link => {
        link.addEventListener('click', event => {
            event.preventDefault();
            company.value = link.dataset.pickCompany;
            company.dispatchEvent(new Event('change'));
            form.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
            company.focus({ preventScroll: true });
        });
    });
    form.addEventListener('submit', () => {
        submit.disabled = true;
        submit.setAttribute('aria-busy', 'true');
        submitLabel.textContent = 'Recording…';
    });
    window.addEventListener('pageshow', event => {
        if(event.persisted){
            submit.disabled = false;
            submit.removeAttribute('aria-busy');
            syncMode();
        }
    });
    if(page.querySelector('#trade-errors')){
        page.querySelector('#trade-errors').focus();
    }
    syncMode();
})();
