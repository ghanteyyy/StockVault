(() => {
    const portfolio = document.querySelector('.sv-portfolio');

    if(!portfolio){
        return;
    }

    const search = portfolio.querySelector('#holdings-search');
    const sectorFilter = portfolio.querySelector('#sector-filter');
    const totalCount = portfolio.querySelector('#holdings-count');
    const visibleCount = portfolio.querySelector('#holdings-visible-count');
    const emptyState = portfolio.querySelector('#holdings-empty');
    const noResults = portfolio.querySelector('#holdings-no-results');
    const clearFilters = portfolio.querySelector('#clear-holdings-filters');
    const notice = portfolio.querySelector('#portfolio-notice');
    const getHoldings = () => [...portfolio.querySelectorAll('.portfolio-item')];

    function applyFilters() {
        const holdings = getHoldings();
        const query = search ? search.value.trim().toLocaleLowerCase() : '';
        const selectedSector = sectorFilter ? sectorFilter.value : '';
        let matches = 0;

        holdings.forEach(holding => {
            const company = (holding.dataset.companyName || '').toLocaleLowerCase();
            const matchesSearch = company.includes(query);
            const matchesSector = !selectedSector || holding.dataset.sector === selectedSector;
            holding.hidden = !(matchesSearch && matchesSector);
            if(!holding.hidden){
                matches += 1;
            }
        });

        if(totalCount){
            totalCount.textContent = holdings.length;
        }
        if(visibleCount){
            const holdingLabel = holdings.length === 1 ? 'holding' : 'holdings';
            visibleCount.textContent = query || selectedSector ?
                `${matches} of ${holdings.length} ${holdingLabel}` :
                `${holdings.length} ${holdingLabel}`;
        }
        if(emptyState){
            emptyState.hidden = holdings.length > 0;
        }
        if(noResults){
            noResults.hidden = holdings.length === 0 || matches > 0;
        }
    }

    function refreshSectors() {
        if(!sectorFilter){
            return;
        }
        const selectedSector = sectorFilter.value;
        const sectors = [...new Set(getHoldings().map(holding => holding.dataset.sector).filter(Boolean))]
            .sort((first, second) => first.localeCompare(second));

        sectorFilter.replaceChildren(new Option('All sectors', ''));
        sectors.forEach(sector => sectorFilter.add(new Option(sector, sector)));
        sectorFilter.value = sectors.includes(selectedSector) ? selectedSector : '';
    }

    function showNotice(message, success) {
        if(!notice){
            return;
        }
        notice.textContent = message;
        notice.hidden = false;
        notice.classList.toggle('is-success', success);
        notice.classList.toggle('is-error', !success);
    }

    function csrfToken() {
        const formToken = portfolio.querySelector('[name="csrfmiddlewaretoken"]');
        if(formToken){
            return formToken.value;
        }
        const cookie = document.cookie.split(';').map(value => value.trim())
            .find(value => value.startsWith('csrftoken='));
        return cookie ? decodeURIComponent(cookie.slice('csrftoken='.length)) : '';
    }

    async function removeHolding(button) {
        const holding = button.closest('.portfolio-item');
        if(!holding || button.disabled || !window.confirm('Remove this opening holding from your portfolio?')){
            return;
        }

        button.disabled = true;
        button.setAttribute('aria-busy', 'true');

        try{
            const response = await fetch(portfolio.dataset.deleteUrl || '/portfolio/delete/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken()
                },
                body: JSON.stringify({
                    company_id: button.dataset.companyId
                })
            });
            const data = await response.json();

            if(!response.ok || !data.status){
                showNotice(data.message || 'Unable to remove this holding. Please try again.', false);
                return;
            }

            const shouldMoveFocus = document.activeElement === button;
            holding.remove();
            refreshSectors();
            applyFilters();
            showNotice(data.message || 'Holding removed successfully.', true);

            if(shouldMoveFocus){
                const nextButton = getHoldings().find(item => !item.hidden)?.querySelector('.holding-remove');
                const focusTarget = nextButton || search || portfolio.querySelector('.portfolio-rail .add-btn');
                if(focusTarget){
                    focusTarget.focus();
                }
            }
        }
        catch (error){
            showNotice('Unable to remove this holding. Please check your connection and try again.', false);
        }
        finally{
            button.disabled = false;
            button.removeAttribute('aria-busy');
        }
    }

    if(search){
        search.addEventListener('input', applyFilters);
    }
    if(sectorFilter){
        sectorFilter.addEventListener('change', applyFilters);
    }
    if(clearFilters){
        clearFilters.addEventListener('click', () => {
            if(search){
                search.value = '';
            }
            if(sectorFilter){
                sectorFilter.value = '';
            }
            applyFilters();
            if(search){
                search.focus();
            }
        });
    }

    portfolio.querySelectorAll('.holding-remove').forEach(button => {
        button.addEventListener('click', () => removeHolding(button));
    });

    refreshSectors();
    applyFilters();
})();
