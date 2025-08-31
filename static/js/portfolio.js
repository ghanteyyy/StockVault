share_numberings = document.querySelectorAll('.share_numbering');

share_numberings.forEach(share_numbering => {
    share_numbering.addEventListener("input", (event)=>{
        event.target.value = event.target.value.replace(/\D/g, "");
    })
});
