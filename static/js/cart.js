document.addEventListener('DOMContentLoaded', function() {
    
    // Get CSRF token from cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    const csrftoken = getCookie('csrftoken');

    // Update quantity buttons
    document.querySelectorAll('.update-quantity').forEach(button => {
        button.addEventListener('click', function () {
            let action = this.getAttribute('data-action');
            let cartItemId = this.getAttribute('data-id');
            let quantityInput = document.querySelector(`#cart-item-${cartItemId} .quantity-input`);
            
    
            fetch(updateCartUrl, {
                method: "POST",
                body: new URLSearchParams({
                    'cart_item_id': cartItemId,
                    'action': action
                }),
                headers: {
                    'X-CSRFToken': csrftoken,
                }
            })
            .then(response => {
                console.log('Fetch response received:', response);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                quantityInput.value = data.new_quantity;
                document.querySelector(`#cart-item-${cartItemId} td:nth-child(4)`).textContent = '₹' + data.new_total.toFixed(2); 
                document.getElementById('cart-total').textContent = 'Total: ₹' + data.total;
    
                // ✅ FIX: Update ALL cart count elements
                document.querySelectorAll('.cart-count').forEach(el => {
                    el.textContent = data.cart_count;
                });
            });
        });
    });

    // Delete cart item buttons
    document.querySelectorAll('.delete-cart-item').forEach(button => {
        button.addEventListener('click', function () {
            let cartItemId = this.getAttribute('data-id');
    
            fetch(deleteCartItemUrl, {
                method: "POST",
                body: new URLSearchParams({
                    'cart_item_id': cartItemId
                }),
                headers: {
                    'X-CSRFToken': csrftoken,
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const itemRow = document.getElementById(`cart-item-${cartItemId}`);
                    if (itemRow) {
                        itemRow.remove();
                    }
    
                    document.getElementById('cart-total').textContent = 'Total: ₹' + data.total;
                    
                    // ✅ FIX: Update ALL cart count elements
                    document.querySelectorAll('.cart-count').forEach(el => {
                        el.textContent = data.cart_count;
                    });
    
                    if (data.cart_count === 0) {
                        window.location.reload();
                    }
                }
            });
        });
    });
    
});