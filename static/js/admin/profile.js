(() => {
    'use strict';

    function initialize() {
        const image = document.querySelector('[data-profile-existing]');
        const fallback = document.querySelector('[data-avatar-fallback]');

        function useFallback() {
            if(image){
                image.hidden = true;
            }
            if(fallback){
                fallback.hidden = false;
            }
        }

        image?.addEventListener('error', useFallback);

        if(image?.complete && !image.naturalWidth){
            useFallback();
        }

        const input = document.querySelector('#profile-image');
        const preview = document.querySelector('[data-photo-preview]');
        const placeholder = document.querySelector('[data-photo-placeholder]');
        const error = document.querySelector('#profile-image-error');

        let url = null;

        function refreshPreview() {
            if(url){
                URL.revokeObjectURL(url);
            }

            url = null;

            if(!input || !preview){
                return;
            }

            preview.hidden = true;
            preview.removeAttribute('src');

            if(placeholder){
                placeholder.hidden = false;
            }

            const file = input.files?.[0];
            const message = file && (!/\.(jpe?g|png)$/i.test(file.name) || file.size > 5 * 1024 * 1024 || !file.size) ?
                'Choose a nonempty JPG or PNG image no larger than 5 MB.' : '';

            if(error){
                error.textContent = message;
                error.hidden = !message;
            }

            if(message){
                input.setAttribute('aria-invalid', 'true');
            }

            else{
                input.removeAttribute('aria-invalid');
            }

            if(file && !message && typeof URL.createObjectURL === 'function'){
                url = URL.createObjectURL(file);
                preview.src = url;
                preview.hidden = false;
                if(placeholder){
                    placeholder.hidden = true;
                }
            }
        }

        input?.addEventListener('change', refreshPreview);

        window.addEventListener('pagehide', () => {
            if(url){
                URL.revokeObjectURL(url);
            }
            url = null;
        });

        window.addEventListener('pageshow', refreshPreview);
    }

    if(document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', initialize, { once: true });
    }

    else{
        initialize();
    }
})();
