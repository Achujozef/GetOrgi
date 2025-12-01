

// Quantity Increase
document.getElementById("increase-quantity").addEventListener("click", function() {
  var quantityInput = document.getElementById("quantity-input");
  var currentQuantity = parseInt(quantityInput.value) || 0;
  quantityInput.value = currentQuantity + 1;
  updateCart('increase');
});

// Quantity Decrease
document.getElementById("decrease-quantity").addEventListener("click", function() {
  var quantityInput = document.getElementById("quantity-input");
  var currentQuantity = parseInt(quantityInput.value) || 0;
  if (currentQuantity > 0) {
    quantityInput.value = currentQuantity - 1;
    updateCart('decrease');
  }
});

// Update Cart
function updateCart(action) {
  var quantityInput = document.getElementById("quantity-input");
  var quantity = parseInt(quantityInput.value);
  var productId = document.getElementById("product_id").value;

  fetch(updateCartUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": csrfToken
    },
    body: new URLSearchParams({
      product_id: productId,
      action: action,
      quantity: quantity
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      console.log(`Cart ${action} successful.`);

      // Update cart count in all locations
      document.querySelectorAll('.cart-count').forEach(el => {
        el.innerText = data.cart_count;
      });

      // Optional: update the quantity input field if returned
      if (data.new_quantity !== undefined) {
        quantityInput.value = data.new_quantity;
      }

    } else if (data.status === 'error' && data.message === 'Please login first.') {
      alert("Please login first.");
      window.location.href = loginUrl;
    }
  });
}

// Star rating behavior
const stars = document.querySelectorAll("#star-rating i");
const ratingInput = document.getElementById("rating");

stars.forEach(star => {
  star.addEventListener("click", function() {
    const ratingValue = this.getAttribute("data-value");
    ratingInput.value = ratingValue;
    
    stars.forEach(s => {
      if (s.getAttribute("data-value") <= ratingValue) {
        s.classList.remove("bi-star");
        s.classList.add("bi-star-fill");
        s.style.color = "gold";
      } else {
        s.classList.remove("bi-star-fill");
        s.classList.add("bi-star");
        s.style.color = "gray";
      }
    });
  });
});

// Submit Review Form
document.getElementById("review-form").addEventListener("submit", function(e) {
  e.preventDefault();

  const productId = document.getElementById("product_id").value;
  const rating = document.getElementById("rating").value;
  const comment = document.getElementById("comment").value;

  if (!rating) {
    alert("Please select a rating by clicking on the stars!");
    return;
  }

  fetch(submitReviewUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": csrfToken
    },
    body: new URLSearchParams({
      product_id: productId,
      rating: rating,
      comment: comment
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      alert("Review submitted successfully!");
      window.location.reload();
    } else {
      alert(data.message);
    }
  });
});
