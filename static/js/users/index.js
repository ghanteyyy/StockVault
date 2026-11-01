(() => {
    function initializeHomepage() {
        const page = document.body;
        if(!page?.classList.contains('sv-home-page')){
            return;
        }

        const panels = [...page.querySelectorAll('[data-tour-panel]')];
        const panelsById = new Map(panels.map(panel => [panel.id, panel]));
        const tabs = [...page.querySelectorAll('[data-tour-tab]')]
            .filter(tab => panelsById.has(tab.getAttribute('aria-controls')));
        if(!tabs.length){
            return;
        }

        function selectTourTab(index, moveFocus = false) {
            const selected = tabs[index];
            const panelId = selected.getAttribute('aria-controls');
            tabs.forEach(tab => {
                const active = tab === selected;
                tab.setAttribute('aria-selected', String(active));
                tab.tabIndex = active ? 0 : -1;
            });
            panels.forEach(panel => {
                panel.hidden = panel.id !== panelId;
            });
            if(moveFocus){
                selected.focus();
            }
        }

        tabs.forEach((tab, index) => {
            tab.addEventListener('click', () => selectTourTab(index));
            tab.addEventListener('keydown', event => {
                if(event.altKey || event.ctrlKey || event.metaKey){
                    return;
                }
                let nextIndex;
                if(event.key === 'ArrowDown' || event.key === 'ArrowRight'){
                    nextIndex = (index + 1) % tabs.length;
                }

                else if(event.key === 'ArrowUp' || event.key === 'ArrowLeft'){
                    nextIndex = (index - 1 + tabs.length) % tabs.length;
                }

                else if(event.key === 'Home'){
                    nextIndex = 0;
                }

                else if(event.key === 'End'){
                    nextIndex = tabs.length - 1;
                }

                else{
                    return;
                }
                event.preventDefault();
                selectTourTab(nextIndex, true);
            });
        });
        const initialTab = tabs.findIndex(tab => tab.getAttribute('aria-selected') === 'true');
        selectTourTab(initialTab >= 0 ? initialTab : 0);
    }

    if(document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', initializeHomepage, { once: true });
    }

    else{
        initializeHomepage();
    }
})();
