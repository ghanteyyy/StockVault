(() => {
    const initialize = () =>
        window.StockVaultAuth?.initialize(document.querySelector("#submit-form"));

    if(document.readyState === "loading"){
        document.addEventListener("DOMContentLoaded", initialize, { once: true });
    }

    else{
        initialize();
    }
})();

const fileInput = document.getElementById('profilePicture');
const svg = document.querySelector(".auth-upload-avatar svg");

fileInput.addEventListener('change', (event) => {
    svg.remove();
});
