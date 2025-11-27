document.addEventListener('DOMContentLoaded', function() {
    
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

    // Prevent navigation when clicking quantity controls
    document.querySelectorAll('.prevent-click').forEach(el => {
        el.addEventListener('click', e => {
            e.stopPropagation();
            e.preventDefault();
        });
    });

    document.querySelectorAll('.product-link').forEach(link => {
        link.addEventListener('click', e => {
            if (e.target.classList.contains('prevent-click') || 
                e.target.closest('.prevent-click')) {
                e.preventDefault();
            }
        });
    });

    // Update Cart Function
    function updateCart(productId, action, inputBox) {
        fetch(updateCartAjaxUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrftoken
            },
            body: new URLSearchParams({
                product_id: productId,
                action: action
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                inputBox.style.transform = 'scale(1.2)';
                inputBox.value = data.new_quantity;
                setTimeout(() => {
                    inputBox.style.transform = 'scale(1)';
                }, 200);

                document.querySelectorAll('.cart-count').forEach(el => {
                    el.innerText = data.cart_count;
                });
            } else if (data.status === 'error' && data.redirect === 'login') {
                window.location.href = "/login";
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Setup quantity controls for each product
    document.querySelectorAll('.product-card').forEach(card => {
        const inputBox = card.querySelector('.quantity-box');
        const productId = inputBox.dataset.productId;
        const decreaseBtn = card.querySelector('.decrease-btn');
        const increaseBtn = card.querySelector('.increase-btn');

        increaseBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            e.preventDefault();
            updateCart(productId, 'increase', inputBox);
        });

        decreaseBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            e.preventDefault();
            if (parseInt(inputBox.value) > 0) {
                updateCart(productId, 'decrease', inputBox);
            }
        });
    });

    // Scroll to Top Button
    const scrollTopBtn = document.getElementById('scrollTop');
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollTopBtn.classList.add('show');
        } else {
            scrollTopBtn.classList.remove('show');
        }
    });

    scrollTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Intersection Observer for Fade-in Animation
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.fade-in-up').forEach(el => {
        observer.observe(el);
    });

    // Add smooth transitions to product cards
    document.querySelectorAll('.product-card').forEach(card => {
        card.style.transition = 'all 0.3s ease';
    });

});

// Category Filter (must be global to work with onclick)
function filterCategory(categoryId, buttonEl) {
    document.querySelectorAll('#category-buttons button').forEach(btn => {
        btn.classList.remove('active');
    });
    buttonEl.classList.add('active');

    document.querySelectorAll('.product-card').forEach(card => {
        const parentCol = card.parentElement;
        if (categoryId === 'all' || card.getAttribute('data-category') === categoryId) {
            parentCol.style.display = 'block';
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 10);
        } else {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {
                parentCol.style.display = 'none';
            }, 300);
        }
    });
}