(() => {
    const page = document.querySelector('.sv-targets');
    if(!page){
        return;
    }

    const form = page.querySelector('#target-form');
    const companyInput = page.querySelector('#target-company-input');
    const suggestions = page.querySelector('#target-company-suggestions');
    const formError = page.querySelector('#target-form-error');
    const cards = [...page.querySelectorAll('.target-card')];
    const search = page.querySelector('#target-search');
    const filters = [...page.querySelectorAll('[data-target-filter]')];
    let activeFilter = 'all';
    let activeSuggestion = -1;
    let suggestionNames = [];
    let companies = [];

    try{
        const parsed = JSON.parse(page.querySelector('#target-companies')?.textContent || '[]');
        companies = Array.isArray(parsed) ? parsed.filter(name => typeof name === 'string') : [];
    }
    catch (error){
        companies = [];
    }

    function clearError(container, message) {
        message.hidden = true;
        message.textContent = '';
        container.querySelectorAll('[aria-invalid="true"]').forEach(field => field.removeAttribute('aria-invalid'));
    }

    function showError(field, message, text) {
        message.textContent = text;
        message.hidden = false;
        field.setAttribute('aria-invalid', 'true');
        field.focus();
        return false;
    }

    function validateRange(lowField, highField, message) {
        const pricePattern = /^(?:\d+(?:\.\d{1,2})?|\.\d{1,2})$/;
        for(const [field, label] of [
                [lowField, 'low'],
                [highField, 'high']
            ]){
            const value = field.value.trim();
            if(!pricePattern.test(value) || !Number.isFinite(Number(value)) || Number(value) <= 0){
                return showError(field, message, `Enter a positive ${label} target with up to two decimal places.`);
            }
        }
        if(Number(lowField.value) >= Number(highField.value)){
            return showError(highField, message, 'High target must be greater than low target.');
        }
        return true;
    }

    function hideSuggestions() {
        suggestions.hidden = true;
        companyInput.setAttribute('aria-expanded', 'false');
        companyInput.removeAttribute('aria-activedescendant');
        activeSuggestion = -1;
    }

    function selectSuggestion(index) {
        const name = suggestionNames[index];
        if(!name){
            return;
        }
        companyInput.value = name;
        clearError(form, formError);
        hideSuggestions();
        companyInput.focus();
    }

    function highlightSuggestion(index) {
        activeSuggestion = index;
        [...suggestions.children].forEach((option, optionIndex) => {
            const selected = optionIndex === index;
            option.setAttribute('aria-selected', String(selected));
            option.classList.toggle('is-active', selected);
        });
        const option = suggestions.children[index];
        if(option){
            companyInput.setAttribute('aria-activedescendant', option.id);
            option.scrollIntoView({ block: 'nearest' });
        }
    }

    function showSuggestions() {
        const query = companyInput.value.trim().toLocaleLowerCase();
        suggestionNames = query ? companies.filter(name => name.toLocaleLowerCase().includes(query)).slice(0, 30) : [];
        suggestions.replaceChildren();
        activeSuggestion = -1;
        companyInput.removeAttribute('aria-activedescendant');
        suggestionNames.forEach((name, index) => {
            const option = document.createElement('button');
            option.type = 'button';
            option.className = 'suggestion-item';
            option.id = `target-company-option-${index}`;
            option.tabIndex = -1;
            option.setAttribute('role', 'option');
            option.setAttribute('aria-selected', 'false');
            option.textContent = name;
            option.addEventListener('mousedown', event => event.preventDefault());
            option.addEventListener('click', () => selectSuggestion(index));
            suggestions.appendChild(option);
        });
        suggestions.hidden = suggestionNames.length === 0;
        companyInput.setAttribute('aria-expanded', String(suggestionNames.length > 0));
    }

    companyInput.setAttribute('role', 'combobox');
    companyInput.setAttribute('aria-autocomplete', 'list');
    companyInput.setAttribute('aria-controls', suggestions.id);
    companyInput.setAttribute('aria-expanded', 'false');
    suggestions.setAttribute('role', 'listbox');
    hideSuggestions();
    companyInput.addEventListener('input', showSuggestions);
    companyInput.addEventListener('focus', () => {
        if(companyInput.value.trim()){
            showSuggestions();
        }
    });
    companyInput.addEventListener('keydown', event => {
        if(event.key === 'Escape'){
            hideSuggestions();
            return;
        }
        if(event.key === 'Tab'){
            hideSuggestions();
            return;
        }
        if(event.key === 'ArrowDown' || event.key === 'ArrowUp'){
            if(suggestions.hidden){
                showSuggestions();
            }
            if(!suggestionNames.length){
                return;
            }
            event.preventDefault();
            const direction = event.key === 'ArrowDown' ? 1 : -1;
            const next = activeSuggestion === -1 ?
                (direction === 1 ? 0 : suggestionNames.length - 1) :
                (activeSuggestion + direction + suggestionNames.length) % suggestionNames.length;
            highlightSuggestion(next);
        }

        else if(event.key === 'Enter' && !suggestions.hidden && activeSuggestion >= 0){
            event.preventDefault();
            selectSuggestion(activeSuggestion);
        }
    });
    document.addEventListener('click', event => {
        if(event.target !== companyInput && !suggestions.contains(event.target)){
            hideSuggestions();
        }
    });

    if(page.hasAttribute('data-focus-targets') && !window.location.hash){
        page.querySelector('.target-backend-errors')?.focus();
    }

    form.addEventListener('input', () => clearError(form, formError));
    form.addEventListener('change', () => clearError(form, formError));
    form.addEventListener('submit', event => {
        clearError(form, formError);
        hideSuggestions();
        const company = companies.find(name => name.toLocaleLowerCase() === companyInput.value.trim().toLocaleLowerCase());
        if(!company){
            event.preventDefault();
            showError(companyInput, formError, 'Choose a company from the current list.');
            return;
        }
        companyInput.value = company;
        const targetType = form.querySelector('input[name="target_type"]:checked');
        if(!targetType || !['buy', 'sell'].includes(targetType.value)){
            event.preventDefault();
            showError(form.querySelector('input[name="target_type"]'), formError, 'Choose a buy or sell target.');
            return;
        }
        if(!validateRange(page.querySelector('#low-target'), page.querySelector('#high-target'), formError)){
            event.preventDefault();
        }
    });

    function numericValue(raw) {
        if(raw === undefined || raw === null || String(raw).trim() === ''){
            return null;
        }
        const value = Number(String(raw).replace(/,/g, '').trim());
        return Number.isFinite(value) ? value : null;
    }

    const priceFormat = new Intl.NumberFormat('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2, });
    page.querySelectorAll('[data-format-price]').forEach(element => {
        const price = numericValue(element.dataset.formatPrice);
        element.textContent = price !== null && price >= 0 ? priceFormat.format(price) : '—';
    });

    cards.forEach(card => {
        const low = numericValue(card.dataset.lowTarget);
        const high = numericValue(card.dataset.highTarget);
        const market = numericValue(card.dataset.marketPrice);
        let status = 'unavailable';
        let position = 50;
        if(low !== null && high !== null && low > 0 && high > low && market !== null && market >= 0){
            status = market < low ? 'below-range' : market > high ? 'above-range' : 'in-range';
            position = Math.max(0, Math.min(100, (market - low) / (high - low) * 100));
        }
        card.dataset.rangeStatus = status;
        card.style.setProperty('--target-position', `${position}%`);
        const statusLabel = card.querySelector('.target-status');
        if(statusLabel){
            statusLabel.textContent = {
                'in-range': 'In range',
                'below-range': 'Below range',
                'above-range': 'Above range',
                unavailable: 'Price unavailable',
            } [status];
        }
        card.querySelectorAll('.target-range-position, .target-range-fill').forEach(indicator => {
            indicator.hidden = status === 'unavailable';
        });
    });

    const setCount = (id, value) => {
        const element = page.querySelector(id);
        if(element){
            element.textContent = value;
        }
    };
    setCount('#target-total-count', cards.length);
    setCount('#target-in-range-count', cards.filter(card => card.dataset.rangeStatus === 'in-range').length);
    setCount('#target-buy-count', cards.filter(card => card.dataset.targetType === 'buy').length);
    setCount('#target-sell-count', cards.filter(card => card.dataset.targetType === 'sell').length);

    function applyFilters() {
        const query = search.value.trim().toLocaleLowerCase();
        let visible = 0;
        cards.forEach(card => {
            const searchable = `${card.dataset.companyName || ''} ${card.dataset.abbreviation || ''}`.toLocaleLowerCase();
            const matchesFilter = activeFilter === 'all' ||
                (activeFilter === 'in-range' ? card.dataset.rangeStatus === 'in-range' : card.dataset.targetType === activeFilter);
            card.hidden = !searchable.includes(query) || !matchesFilter;
            if(!card.hidden){
                visible += 1;
            }
        });
        const filtered = query || activeFilter !== 'all';
        const label = cards.length === 1 ? 'target' : 'targets';
        setCount('#target-visible-count', filtered ? `${visible} of ${cards.length} ${label}` : `${cards.length} ${label}`);
        const empty = page.querySelector('#targets-empty');
        const noResults = page.querySelector('#targets-no-results');
        if(empty){
            empty.hidden = cards.length > 0;
        }
        if(noResults){
            noResults.hidden = cards.length === 0 || visible > 0;
        }
        filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.targetFilter === activeFilter)));
    }
    search.addEventListener('input', applyFilters);
    filters.forEach(button => button.addEventListener('click', () => {
        activeFilter = button.dataset.targetFilter;
        applyFilters();
    }));
    page.querySelector('#clear-target-filters')?.addEventListener('click', () => {
        search.value = '';
        activeFilter = 'all';
        applyFilters();
        search.focus();
    });
    applyFilters();

    const editDialog = page.querySelector('#edit-target-dialog');
    const editForm = page.querySelector('#edit-target-form');
    const editError = page.querySelector('#edit-target-error');
    const editLow = page.querySelector('#edit_low_target');
    const editHigh = page.querySelector('#edit_high_target');
    const deleteDialog = page.querySelector('#delete-target-dialog');
    const deleteForm = page.querySelector('#delete-target-form');
    const dialogOpeners = new WeakMap();

    function openDialog(dialog, opener) {
        hideSuggestions();
        dialogOpeners.set(dialog, opener);
        dialog.showModal();
    }

    page.querySelectorAll('.target-edit').forEach(button => button.addEventListener('click', () => {
        clearError(editForm, editError);
        page.querySelector('#edit-target-id').value = button.dataset.targetId;
        page.querySelector('#edit_company_abbr').value = button.dataset.abbreviation;
        page.querySelector('#edit-company-name').textContent = button.dataset.companyName;
        page.querySelector('#edit-target-type').textContent = `${button.dataset.targetType === 'sell' ? 'Sell' : 'Buy'} target`;
        editLow.value = String(numericValue(button.dataset.lowTarget) ?? '');
        editHigh.value = String(numericValue(button.dataset.highTarget) ?? '');
        openDialog(editDialog, button);
        editLow.focus();
    }));
    editForm.addEventListener('input', () => clearError(editForm, editError));
    editForm.addEventListener('submit', event => {
        clearError(editForm, editError);
        if(!validateRange(editLow, editHigh, editError)){
            event.preventDefault();
        }
    });

    page.querySelectorAll('.target-delete').forEach(button => button.addEventListener('click', () => {
        page.querySelector('#delete-target-id').value = button.dataset.targetId;
        page.querySelector('#delete-company-name').textContent = button.dataset.companyName;
        page.querySelector('#delete-target-type').textContent = `${button.dataset.targetType === 'sell' ? 'sell' : 'buy'} target`;
        deleteForm.action = button.dataset.deleteUrl;
        openDialog(deleteDialog, button);
    }));

    [editDialog, deleteDialog].forEach(dialog => {
        dialog.querySelectorAll('[data-close-dialog]').forEach(button => button.addEventListener('click', () => dialog.close()));
        dialog.addEventListener('click', event => {
            if(event.target !== dialog){
                return;
            }
            const rect = dialog.getBoundingClientRect();
            if(event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom){
                dialog.close();
            }
        });
        dialog.addEventListener('close', () => dialogOpeners.get(dialog)?.focus());
    });
})();
