(() => {
    const page = document.querySelector('.sv-wishlist');
    if(!page){
        return;
    }

    const form = page.querySelector('#wishlist-form');
    const companyInput = page.querySelector('#stock-input');
    const addButton = page.querySelector('#add-btn');
    const suggestions = page.querySelector('#suggestions');
    const formError = page.querySelector('#wishlist-form-error');
    const availability = page.querySelector('#wishlist-availability-text');
    const grid = page.querySelector('#wishlist-grid');
    const cards = [...page.querySelectorAll('.wishlist-card')];
    const search = page.querySelector('#wishlist-search');
    const sectorFilter = page.querySelector('#wishlist-sector-filter');
    const sort = page.querySelector('#wishlist-sort');
    const uncategorized = '__uncategorized__';
    const normalize = value => String(value || '').trim().toLocaleLowerCase();
    let companies = [];
    let catalogAvailable = true;
    let suggestedCompanies = [];
    let activeSuggestion = -1;

    try{
        const data = JSON.parse(page.querySelector('#wishlist-companies')?.textContent || 'null');
        if(!Array.isArray(data)){
            throw new Error('Invalid company list');
        }
        companies = data.filter(company => company && typeof company.name === 'string' && company.name.trim())
            .map(company => ({
                name: company.name.trim(),
                abbreviation: typeof company.abbreviation === 'string' ? company.abbreviation.trim() : '',
                sector: typeof company.sector === 'string' ? company.sector.trim() : '',
            }));
    }
    catch (error){
        catalogAvailable = false;
    }

    function clearError() {
        formError.hidden = true;
        formError.textContent = '';
        companyInput.removeAttribute('aria-invalid');
    }

    function showError(message) {
        formError.textContent = message;
        formError.hidden = false;
        companyInput.setAttribute('aria-invalid', 'true');
        if(!companyInput.disabled){
            companyInput.focus();
        }
    }

    function hideSuggestions() {
        suggestions.hidden = true;
        companyInput.setAttribute('aria-expanded', 'false');
        companyInput.removeAttribute('aria-activedescendant');
        activeSuggestion = -1;
    }

    function selectSuggestion(index) {
        const company = suggestedCompanies[index];
        if(!company){
            return;
        }
        companyInput.value = company.name;
        clearError();
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
            option.scrollIntoView?.({ block: 'nearest' });
        }
    }

    function showSuggestions(includeAll = false) {
        if(companyInput.disabled){
            return;
        }
        const query = normalize(companyInput.value);
        suggestedCompanies = query || includeAll ?
            companies.filter(company => normalize(company.name).includes(query) ||
                normalize(company.abbreviation).includes(query)).slice(0, 30) : [];
        suggestions.replaceChildren();
        companyInput.removeAttribute('aria-activedescendant');
        activeSuggestion = -1;

        suggestedCompanies.forEach((company, index) => {
            const option = document.createElement('button');
            option.type = 'button';
            option.className = 'wishlist-suggestion';
            option.id = `wishlist-company-option-${index}`;
            option.tabIndex = -1;
            option.setAttribute('role', 'option');
            option.setAttribute('aria-selected', 'false');

            const name = document.createElement('span');
            name.className = 'suggestion-company-name';
            name.textContent = company.name;
            const symbol = document.createElement('span');
            symbol.className = 'suggestion-company-symbol';
            symbol.textContent = company.abbreviation;
            const sector = document.createElement('span');
            sector.className = 'suggestion-company-sector';
            sector.textContent = company.sector || 'Uncategorized';
            option.append(name, symbol, sector);
            option.addEventListener('mousedown', event => event.preventDefault());
            option.addEventListener('click', () => selectSuggestion(index));
            suggestions.appendChild(option);
        });

        suggestions.hidden = suggestedCompanies.length === 0;
        companyInput.setAttribute('aria-expanded', String(suggestedCompanies.length > 0));
    }

    companyInput.setAttribute('role', 'combobox');
    companyInput.setAttribute('aria-autocomplete', 'list');
    companyInput.setAttribute('aria-controls', 'suggestions');
    suggestions.setAttribute('role', 'listbox');
    companyInput.disabled = !companies.length;
    addButton.disabled = !companies.length;
    if(!catalogAvailable && availability){
        availability.textContent = 'Company search is temporarily unavailable. Refresh the page and try again.';
    }
    hideSuggestions();

    companyInput.addEventListener('input', () => {
        clearError();
        showSuggestions();
    });
    companyInput.addEventListener('focus', () => {
        if(companyInput.value.trim()){
            showSuggestions();
        }
    });
    companyInput.addEventListener('keydown', event => {
        if(event.key === 'Escape' || event.key === 'Tab'){
            hideSuggestions();
            return;
        }
        if(event.key === 'ArrowDown' || event.key === 'ArrowUp'){
            if(suggestions.hidden){
                showSuggestions(true);
            }
            if(!suggestedCompanies.length){
                return;
            }
            event.preventDefault();
            const direction = event.key === 'ArrowDown' ? 1 : -1;
            const next = activeSuggestion === -1 ?
                (direction === 1 ? 0 : suggestedCompanies.length - 1) :
                (activeSuggestion + direction + suggestedCompanies.length) % suggestedCompanies.length;
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

    form.addEventListener('submit', event => {
        clearError();
        hideSuggestions();
        const query = normalize(companyInput.value);
        const namedCompany = companies.find(company => normalize(company.name) === query);
        const symbolMatches = companies.filter(company => normalize(company.abbreviation) === query);
        const company = namedCompany || (symbolMatches.length === 1 ? symbolMatches[0] : null);
        if(!company){
            event.preventDefault();
            const alreadySaved = query && cards.some(card => normalize(card.dataset.companyName) === query ||
                normalize(card.dataset.abbreviation) === query);
            showError(alreadySaved ? 'This company is already in your wishlist.' :
                'Choose a company from the available list.');
            return;
        }
        companyInput.value = company.name;
    });

    const sectorValue = card => String(card.dataset.sector || '').trim();
    const sectors = [...new Set(cards.map(sectorValue).filter(Boolean))].sort((first, second) => first.localeCompare(second));
    const previousSector = sectorFilter.value;
    sectorFilter.replaceChildren(new Option('All sectors', ''));
    sectors.forEach(sector => sectorFilter.add(new Option(sector, sector)));
    if(cards.some(card => !sectorValue(card))){
        sectorFilter.add(new Option('Uncategorized', uncategorized));
    }
    sectorFilter.value = sectors.includes(previousSector) || previousSector === uncategorized ? previousSector : '';

    function setText(id, value) {
        const element = page.querySelector(id);
        if(element){
            element.textContent = value;
        }
    }
    setText('#wishlist-total-count', cards.length);
    setText('#wishlist-sector-count', sectors.length);

    function applyFilters() {
        const query = normalize(search.value);
        const sector = sectorFilter.value;
        let visible = 0;
        cards.forEach(card => {
            const haystack = `${card.dataset.companyName || ''} ${card.dataset.abbreviation || ''}`.toLocaleLowerCase();
            const matchesSector = !sector || (sector === uncategorized ? !sectorValue(card) : sectorValue(card) === sector);
            card.hidden = !haystack.includes(query) || !matchesSector;
            if(!card.hidden){
                visible += 1;
            }
        });
        const filtered = Boolean(query || sector);
        const companyLabel = cards.length === 1 ? 'company' : 'companies';
        setText('#wishlist-visible-count', filtered ?
            `${visible} of ${cards.length} ${companyLabel}` : `${cards.length} ${companyLabel}`);
        const empty = page.querySelector('#wishlist-empty');
        const noResults = page.querySelector('#wishlist-no-results');
        if(empty){
            empty.hidden = cards.length > 0;
        }
        if(noResults){
            noResults.hidden = cards.length === 0 || visible > 0;
        }
    }

    function sortCards() {
        const direction = sort.value === 'desc' ? -1 : 1;
        [...cards].sort((first, second) => direction * String(first.dataset.companyName || '')
                .localeCompare(String(second.dataset.companyName || ''), undefined, { sensitivity: 'base' }))
            .forEach(card => grid.appendChild(card));
    }
    search.addEventListener('input', applyFilters);
    sectorFilter.addEventListener('change', applyFilters);
    sort.addEventListener('change', () => {
        sortCards();
        applyFilters();
    });
    page.querySelector('#clear-wishlist-filters')?.addEventListener('click', () => {
        search.value = '';
        sectorFilter.value = '';
        applyFilters();
        search.focus();
    });
    sortCards();
    applyFilters();

    function focusCompany(event) {
        event.preventDefault();
        hideSuggestions();
        if(companyInput.disabled){
            if(availability){
                availability.tabIndex = -1;
                availability.focus();
            }
            return;
        }
        companyInput.focus();
        companyInput.scrollIntoView?.({ block: 'center' });
    }
    page.querySelectorAll('.wishlist-empty-action, #jump-to-wishlist-form').forEach(button => {
        button.addEventListener('click', focusCompany);
    });

    const dialog = page.querySelector('#remove-wishlist-dialog');
    let removeOpener = null;
    page.querySelectorAll('.wishlist-remove').forEach(button => button.addEventListener('click', () => {
        hideSuggestions();
        page.querySelector('#wishlist-remove-id').value = button.dataset.wishlistId;
        page.querySelector('#wishlist-remove-company').textContent = button.dataset.companyName;
        page.querySelector('#wishlist-remove-symbol').textContent = button.dataset.abbreviation;
        removeOpener = button;
        dialog.showModal();
    }));
    dialog.querySelectorAll('[data-close-dialog]').forEach(button => {
        button.addEventListener('click', () => dialog.close());
    });
    dialog.addEventListener('click', event => {
        if(event.target !== dialog){
            return;
        }
        const rect = dialog.getBoundingClientRect();
        if(event.clientX < rect.left || event.clientX > rect.right ||
            event.clientY < rect.top || event.clientY > rect.bottom){
            dialog.close();
        }
    });
    dialog.addEventListener('close', () => removeOpener?.focus());
})();
