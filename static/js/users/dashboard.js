const items = document.querySelectorAll(".sidebar div ul li");

items.forEach(item => {
	item.addEventListener("click", () => {
		items.forEach(i => i.classList.remove("active"));
		item.classList.add("active");
		document.querySelector(".main-content > div:first-child h1").textContent = item.textContent.trim();
	});
});
