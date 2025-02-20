// Cart management
let cart = JSON.parse(localStorage.getItem('cart')) || {};

function updateCart() {
    const cartItems = document.getElementById('cart-items');
    const template = document.getElementById('cart-item-template');
    const total = document.getElementById('cart-total');
    
    if (cartItems) {
        cartItems.innerHTML = '';
        let totalAmount = 0;
        
        Object.values(cart).forEach(item => {
            const clone = template.content.cloneNode(true);
            
            clone.querySelector('.product-name').textContent = item.name;
            clone.querySelector('.product-price').textContent = `$${item.price.toFixed(2)}`;
            clone.querySelector('img').src = item.image;
            clone.querySelector('.quantity-input').value = item.quantity;
            
            const removeBtn = clone.querySelector('.remove-item');
            removeBtn.onclick = () => removeFromCart(item.id);
            
            const decreaseBtn = clone.querySelector('.decrease-quantity');
            decreaseBtn.onclick = () => updateQuantity(item.id, item.quantity - 1);
            
            const increaseBtn = clone.querySelector('.increase-quantity');
            increaseBtn.onclick = () => updateQuantity(item.id, item.quantity + 1);
            
            totalAmount += item.price * item.quantity;
            cartItems.appendChild(clone);
        });
        
        total.textContent = totalAmount.toFixed(2);
    }
    
    // Update checkout page if it exists
    const checkoutItems = document.getElementById('checkout-items');
    const checkoutTotal = document.getElementById('checkout-total');
    if (checkoutItems && checkoutTotal) {
        checkoutItems.innerHTML = '';
        let totalAmount = 0;
        
        Object.values(cart).forEach(item => {
            const div = document.createElement('div');
            div.className = 'd-flex justify-content-between mb-2';
            div.innerHTML = `
                <span>${item.name} x ${item.quantity}</span>
                <span>$${(item.price * item.quantity).toFixed(2)}</span>
            `;
            checkoutItems.appendChild(div);
            totalAmount += item.price * item.quantity;
        });
        
        checkoutTotal.textContent = `$${totalAmount.toFixed(2)}`;
    }
}

function addToCart(productId) {
    fetch(`/products/${productId}`)
        .then(response => response.json())
        .then(product => {
            if (cart[product.id]) {
                cart[product.id].quantity += 1;
            } else {
                cart[product.id] = {
                    id: product.id,
                    name: product.name,
                    price: product.price,
                    image: product.image,
                    quantity: 1
                };
            }
            localStorage.setItem('cart', JSON.stringify(cart));
            updateCart();
        });
}

function updateQuantity(productId, quantity) {
    if (quantity < 1) {
        removeFromCart(productId);
        return;
    }
    
    cart[productId].quantity = quantity;
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCart();
}

function removeFromCart(productId) {
    delete cart[productId];
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCart();
}

function clearCart() {
    cart = {};
    localStorage.removeItem('cart');
    updateCart();
}

// Initialize cart on page load
document.addEventListener('DOMContentLoaded', () => {
    updateCart();
    
    // Add event listeners to "Add to Cart" buttons
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', () => {
            const productId = button.dataset.productId;
            addToCart(productId);
        });
    });
});
