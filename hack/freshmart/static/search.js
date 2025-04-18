document.addEventListener('DOMContentLoaded', () => {
    const searchBtn = document.getElementById('searchBtn');
    if (searchBtn) {
        searchBtn.addEventListener('click', searchAll);
    }
});

function searchAll() {
    const input = document.getElementById('searchInput').value.toLowerCase();
    const storeCards = document.querySelectorAll('.store-card');
    const productsSection = document.getElementById('productsSection');
    const productsContainer = document.getElementById('productsContainer');

    const isProductsVisible = productsSection && productsSection.style.display !== 'none';

    if (!isProductsVisible) {
        storeCards.forEach(card => {
            const storeName = card.getAttribute('data-store-name').toLowerCase();
            const storeArea = card.getAttribute('data-store-area').toLowerCase();
            const match = storeName.includes(input) || storeArea.includes(input);
            card.style.display = match ? 'block' : 'none';
        });
    } else {
        const productCards = productsContainer.querySelectorAll('.product-card');
        let found = false;
        productCards.forEach(card => {
            const name = card.querySelector('.product-name').textContent.toLowerCase();
            const match = name.includes(input);
            card.style.display = match ? 'block' : 'none';
            if (match) found = true;
        });

        if (!found) {
            const noResultsMessage = document.createElement('p');
            noResultsMessage.textContent = `No products found matching "${input}".`;
            noResultsMessage.style.color = 'red';
            productsContainer.innerHTML = '';
            productsContainer.appendChild(noResultsMessage);
        }
    }
}
