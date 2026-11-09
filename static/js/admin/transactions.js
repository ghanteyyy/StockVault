(() => {
    'use strict';

    const tradeForm = document.querySelector('[data-trade-form]');
    const openingForm = document.querySelector('[data-opening-form]');
    const deleteForm = document.querySelector('[data-delete-form]');

    function showField(form, selector, visible, required = false) {
        const group = form.querySelector(selector);
        const field = group.querySelector('input, select');
        group.hidden = !visible;
        field.disabled = !visible;
        field.required = visible && required;
    }

    function updateTradeFields() {
        const kind = tradeForm.elements.namedItem('transaction_type').value;
        const historical = tradeForm.dataset.legacy === 'yes';
        showField(tradeForm, '[data-unit-price-field]', !historical && kind !== 'bonus', true);
        showField(tradeForm, '[data-legacy-amount-field]', historical, true);
        showField(tradeForm, '[data-purchase-type-field]', !historical && kind === 'buy');
        showField(tradeForm, '[data-cgt-field]', !historical && kind === 'sell');
        tradeForm.querySelector('[data-legacy-warning]').hidden = !historical;
        const hint = tradeForm.querySelector('[data-trade-hint]');
        hint.hidden = historical;

        if(kind === 'bonus'){
            hint.textContent = 'Bonus shares increase the quantity held. The total purchase cost stays the same.';
        }

        else if(kind === 'sell'){
            hint.textContent = 'The sale uses the holding’s weighted average cost and deducts the configured charges and tax.';
        }

        else{
            hint.textContent = 'A purchase increases the number of shares and adds its full acquisition cost.';
        }
    }

    function prepareForm(form, button, title, submit) {
        const editing = button.hasAttribute('data-record-edit');
        form.reset();
        form.querySelector('[data-record-id]').value = button.dataset.id || '';
        form.closest('dialog').querySelector('[data-record-title]').textContent = title;
        form.querySelector('[data-record-submit]').textContent = submit;

        for(const name of ['user_id', 'company_id']){
            const field = form.elements.namedItem(name);
            field.disabled = editing;
        }
        form.elements.namedItem('user_id').value = button.dataset.member || '';
        form.elements.namedItem('company_id').value = button.dataset.company || '';
    }

    if(tradeForm){
        tradeForm.elements.namedItem('transaction_type').addEventListener('change', updateTradeFields);
        document.querySelectorAll('[data-dialog-open="transaction-dialog"]').forEach(button => {
            button.addEventListener('click', () => {
                const editing = button.hasAttribute('data-record-edit');
                prepareForm(tradeForm, button, editing ? 'Edit transaction' : 'Record transaction', editing ? 'Save changes' : 'Record transaction');
                tradeForm.action = editing ? tradeForm.dataset.editUrl : tradeForm.dataset.addUrl;
                tradeForm.dataset.legacy = button.dataset.legacy || 'no';

                if(editing){
                    tradeForm.elements.namedItem('transaction_type').value = button.dataset.type;
                    tradeForm.elements.namedItem('quantity').value = button.dataset.quantity;
                    tradeForm.elements.namedItem('unit_price').value = button.dataset.price;
                    tradeForm.elements.namedItem('legacy_amount').value = button.dataset.amount;
                    tradeForm.elements.namedItem('transaction_date').value = button.dataset.date;
                    tradeForm.elements.namedItem('purchase_type').value = button.dataset.purchase;
                    tradeForm.elements.namedItem('cgt_type').value = button.dataset.cgt;
                    tradeForm.elements.namedItem('notes').value = button.dataset.notes;
                }
                updateTradeFields();
            });
        });
    }

    if(openingForm){
        document.querySelectorAll('[data-dialog-open="holding-dialog"]').forEach(button => {
            button.addEventListener('click', () => {
                const editing = button.hasAttribute('data-record-edit');
                prepareForm(openingForm, button, editing ? 'Edit opening balance' : 'Add opening holding', 'Save opening balance');
                openingForm.elements.namedItem('quantity').value = button.dataset.quantity || '';
                openingForm.elements.namedItem('total_cost').value = button.dataset.cost || '';
            });
        });
    }

    if(deleteForm){
        document.querySelectorAll('[data-record-delete]').forEach(button => {
            button.addEventListener('click', () => {
                deleteForm.querySelector('[data-record-id]').value = button.dataset.id;
                deleteForm.querySelector('[data-record-label]').textContent = button.dataset.label;
                const ledgerMessage = deleteForm.querySelector('[data-delete-ledger]');
                const historyMessage = deleteForm.querySelector('[data-delete-history]');

                if(ledgerMessage && historyMessage){
                    const historical = button.dataset.legacy === 'yes';
                    ledgerMessage.hidden = historical;
                    historyMessage.hidden = !historical;
                }
            });
        });
    }
})();
