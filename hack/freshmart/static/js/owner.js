// Basic JavaScript functions for demonstration purposes

function addProduct() {
    const name = document.getElementById('addProductName').value;
    const price = document.getElementById('addProductPrice').value;
    const category = document.getElementById('addProductCategory').value;
    if (name && price && category) {
        const productList = document.querySelector('.product-list');
        const newProduct = document.createElement('li');
        newProduct.className = 'product-item';
        newProduct.dataset.productId = name.toLowerCase().replace(' ', '-');
        newProduct.innerHTML = `
            <span>${name} - ₹${price} (${category})</span>
            <div class="controls">
                <button onclick="editProduct('${newProduct.dataset.productId}')">Edit</button>
                <button onclick="deleteProduct('${newProduct.dataset.productId}')">Delete</button>
            </div>
        `;
        productList.appendChild(newProduct);
        document.getElementById('addProductName').value = '';
        document.getElementById('addProductPrice').value = '';
        document.getElementById('addProductCategory').value = '';
        alert('Product added!');
    } else {
        alert('Please fill in all product details.');
    }
}

function editProduct(productId) {
    alert(`Editing product: ${productId}`);
    // Implement edit functionality (e.g., show a form to modify product details)
}

function deleteProduct(productId) {
    if (confirm(`Are you sure you want to delete ${productId}?`)) {
        const productItem = document.querySelector(`.product-item[data-product-id="${productId}"]`);
        if (productItem) {
            productItem.remove();
            alert(`${productId} deleted.`);
        }
    }
}

function adjustStock(productName, quantityChange) {
    alert(`Adjusting stock for ${productName} by ${quantityChange}`);
    // Implement stock adjustment logic (update the table)
}

function updateStock() {
    const productName = document.getElementById('updateProductName').value;
    const quantityChange = parseInt(document.getElementById('updateQuantity').value);
    if (productName && !isNaN(quantityChange)) {
        alert(`Updating stock for ${productName} by ${quantityChange}`);
        // Implement stock update logic based on product name
        document.getElementById('updateProductName').value = '';
        document.getElementById('updateQuantity').value = '';
    } else {
        alert('Please enter product name and a valid quantity.');
    }
}

function deleteStore(storeId) {
    if (confirm(`Are you sure you want to delete store ID ${storeId}?`)) {
        window.location.href = `/delete_store/${storeId}/`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const addProductForms = document.querySelectorAll('#addProductForm');
    const productList = document.getElementById('productList');
    const successMessage = document.getElementById('successMessage');

    addProductForms.forEach((form) => {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();

            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            if (response.ok) {
                const newProduct = await response.json();
                const productItem = document.createElement('li');
                productItem.className = 'product-item';
                productItem.dataset.productId = newProduct.id;
                productItem.innerHTML = `
                    <span>${newProduct.name} - ₹${newProduct.price}</span>
                    <div class="controls">
                        <button onclick="editProduct('${newProduct.id}')">Edit</button>
                        <button onclick="deleteProduct('${newProduct.id}')">Delete</button>
                    </div>
                `;
                productList.appendChild(productItem);

                successMessage.style.display = 'block';
                setTimeout(() => {
                    successMessage.style.display = 'none';
                }, 3000);

                form.reset();
            } else {
                alert('Failed to add product. Please try again.');
            }
        });
    });

    const sellButtons = document.querySelectorAll('.sell-product-btn');
    const addButtons = document.querySelectorAll('.add-stock-btn');

    sellButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
            event.preventDefault();
            const productId = button.dataset.productId;
            const quantityChange = parseInt(button.dataset.quantityChange);

            try {
                const response = await fetch('/adjust-quantity/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                    },
                    body: JSON.stringify({ product_id: productId, quantity_change: quantityChange }),
                });

                if (response.ok) {
                    const data = await response.json();
                    updateInventoryUI(data.id, data.quantity, data.sold_quantity);
                } else {
                    const errorData = await response.json();
                    alert(`Failed to sell product: ${errorData.error}`);
                }
            } catch (error) {
                alert('An error occurred while selling the product. Please try again.');
            }
        });
    });

    addButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
            event.preventDefault();
            const productId = button.dataset.productId;
            const quantityChange = parseInt(button.dataset.quantityChange);

            try {
                const response = await fetch('/adjust-quantity/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                    },
                    body: JSON.stringify({ product_id: productId, quantity_change: quantityChange }),
                });

                if (response.ok) {
                    const data = await response.json();
                    updateInventoryUI(data.id, data.quantity, data.sold_quantity);
                } else {
                    const errorData = await response.json();
                    alert(`Failed to add stock: ${errorData.error}`);
                }
            } catch (error) {
                alert('An error occurred while adding stock. Please try again.');
            }
        });
    });

    function updateInventoryUI(productId, quantity, soldQuantity) {
        const quantityElement = document.querySelector(`#product-quantity-${productId}`);
        const soldQuantityElement = document.querySelector(`#product-sold-quantity-${productId}`);
        if (quantityElement) quantityElement.textContent = `${quantity}`;
        if (soldQuantityElement) soldQuantityElement.textContent = `${soldQuantity}`;
        if (quantityElement) quantityElement.className = getStockLevelClass(quantity);
    }

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function getStockLevelClass(quantity) {
        if (quantity === 0) return 'stock-level out-of-stock';
        if (quantity < 10) return 'stock-level low-stock';
        return 'stock-level in-stock';
    }
});
