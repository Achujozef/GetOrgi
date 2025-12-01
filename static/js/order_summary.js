// document.addEventListener("DOMContentLoaded", function () {
//     const options = {
//         "key": rzp_key,
//         "amount": parseInt(grand_total * 100),
//         "currency": "INR",
//         "name": "GetOrgi",
//         "description": "Order Payment",
//         "order_id": rzp_order_id,
//         "handler": function (response) {
//             document.getElementById('paymentLoading').classList.add('active');
//             document.getElementById('rzp-button1').style.display = 'none';

//             fetch(verify_payment_url, {
//                 method: "POST",
//                 headers: {
//                     "Content-Type": "application/json",
//                     "X-CSRFToken": csrf_token
//                 },
//                 body: JSON.stringify({
//                     razorpay_order_id: response.razorpay_order_id,
//                     razorpay_payment_id: response.razorpay_payment_id,
//                     razorpay_signature: response.razorpay_signature
//                 })
//             })
//             .then(res => res.json())
//             .then(data => {
//                 if (data.status === "success") {
//                     document.getElementById('paymentLoading').innerHTML = `
//                         <div style="color: var(--primary-green); text-align:center;">
//                             <i class="fas fa-check-circle" style="font-size:4rem; margin-bottom:20px;"></i>
//                             <h4>Payment Successful!</h4>
//                             <p>Your order has been placed successfully. Thank you for shopping with GetOrgi!</p>
//                         </div>
//                     `;
//                     document.querySelectorAll('.progress-step').forEach(step => step.classList.add('inactive'));
//                     document.querySelector('.progress-step:last-child').classList.remove('inactive');

//                     setTimeout(() => {
//                         window.location.href = data.redirect_url || '/my-orders/';
//                     }, 2000);

//                 } else {
//                     document.getElementById('paymentLoading').innerHTML = `
//                         <div style="color: #dc3545; text-align:center;">
//                             <i class="fas fa-times-circle" style="font-size:4rem; margin-bottom:20px;"></i>
//                             <h4>Payment Failed!</h4>
//                             <p>Please try again or contact support.</p>
//                         </div>
//                     `;
//                     document.getElementById('rzp-button1').style.display = 'inline-block';
//                 }
//             })
//             .catch(err => {
//                 console.error(err);
//                 document.getElementById('paymentLoading').innerHTML = `
//                     <div style="color: #dc3545; text-align:center;">
//                         <i class="fas fa-exclamation-circle" style="font-size:4rem; margin-bottom:20px;"></i>
//                         <h4>Error!</h4>
//                         <p>Something went wrong. Please refresh and try again.</p>
//                     </div>
//                 `;
//                 document.getElementById('rzp-button1').style.display = 'inline-block';
//             });
//         },
//         "prefill": {
//             "name": customer_name,
//             "email": user_email,
//             "contact": customer_phone
//         },
//         "theme": {
//             "color": "#198754"
//         }
//     };

//     const rzp1 = new Razorpay(options);
//     document.getElementById('rzp-button1').onclick = function (e) {
//         rzp1.open();
//         e.preventDefault();
//     };
// });

document.addEventListener("DOMContentLoaded", function () {
    const options = {
        "key": rzp_key,
        "amount": parseInt(grand_total * 100),
        "currency": "INR",
        "name": "GetOrgi",
        "description": "Order Payment",
        "order_id": rzp_order_id,
        "handler": function (response) {
            // Show loading state
            document.getElementById('paymentLoading').classList.add('active');
            document.getElementById('rzp-button1').style.display = 'none';

            fetch(verify_payment_url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrf_token
                },
                body: JSON.stringify({
                    razorpay_order_id: response.razorpay_order_id,
                    razorpay_payment_id: response.razorpay_payment_id,
                    razorpay_signature: response.razorpay_signature
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    // Show success message
                    document.getElementById('paymentLoading').innerHTML = `
                        <div style="color: var(--primary-green); text-align:center;">
                            <i class="fas fa-check-circle" style="font-size:4rem; margin-bottom:20px;"></i>
                            <h4>Payment Successful!</h4>
                            <p>Your order has been placed successfully. Thank you for shopping with GetOrgi!</p>
                            <p style="color: #666; font-size: 0.9rem; margin-top: 10px;">Redirecting...</p>
                        </div>
                    `;
                    
                    // Update progress indicator
                    document.querySelectorAll('.progress-step').forEach(step => step.classList.remove('inactive'));
                    
                    // Redirect after 2 seconds
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 2000);

                } else {
                    // Show failure message
                    document.getElementById('paymentLoading').classList.remove('active');
                    document.getElementById('paymentLoading').innerHTML = `
                        <div style="color: #dc3545; text-align:center; padding: 20px;">
                            <i class="fas fa-times-circle" style="font-size:4rem; margin-bottom:20px;"></i>
                            <h4>Payment Verification Failed!</h4>
                            <p>Please try again or contact support.</p>
                        </div>
                    `;
                    document.getElementById('rzp-button1').style.display = 'inline-block';
                }
            })
            .catch(err => {
                console.error("Payment verification error:", err);
                document.getElementById('paymentLoading').classList.remove('active');
                document.getElementById('paymentLoading').innerHTML = `
                    <div style="color: #dc3545; text-align:center; padding: 20px;">
                        <i class="fas fa-exclamation-circle" style="font-size:4rem; margin-bottom:20px;"></i>
                        <h4>Error!</h4>
                        <p>Something went wrong. Please refresh and try again.</p>
                    </div>
                `;
                document.getElementById('rzp-button1').style.display = 'inline-block';
            });
        },
        "modal": {
            "ondismiss": function() {
                // Handle when user closes the payment modal
                console.log("Payment modal closed by user");
            }
        },
        "prefill": {
            "name": customer_name,
            "email": user_email,
            "contact": customer_phone
        },
        "theme": {
            "color": "#198754"
        }
    };

    const rzp1 = new Razorpay(options);
    
    document.getElementById('rzp-button1').onclick = function (e) {
        e.preventDefault();
        rzp1.open();
    };
});