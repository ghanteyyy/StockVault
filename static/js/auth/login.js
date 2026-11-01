(() => {
    const initialize = () => window.StockVaultAuth?.initialize(document.querySelector('#login_form'));
    if(document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', initialize, { once: true });
    }

    else{
        initialize();
    }
})();
