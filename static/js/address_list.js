// Make full card clickable except the Edit button
document.addEventListener("DOMContentLoaded", function () {
    
    // Card click selection
    document.querySelectorAll('.address-card').forEach(card => {
        card.addEventListener('click', function (e) {
            if (!e.target.closest('.edit-address-btn')) {
                const checkbox = this.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    // Uncheck all others
                    document.querySelectorAll('.address-checkbox')
                        .forEach(cb => cb.checked = false);

                    // Check this one
                    checkbox.checked = true;

                    // Enable Continue button
                    document.getElementById('continue-button').disabled = false;

                    // Set selected ID
                    document.getElementById('selected-address-id').value = checkbox.dataset.id;
                }
            }
        });
    });

    // Pre-fill edit modal
    document.querySelectorAll('.edit-address-btn').forEach(button => {
        button.addEventListener('click', function () {
            document.getElementById('edit-address-id').value = this.dataset.id;
            document.getElementById('edit-customer-name').value = this.dataset.customer_name;
            document.getElementById('edit-full-address').value = this.dataset.full_address;
            document.getElementById('edit-landmark').value = this.dataset.landmark;
            document.getElementById('edit-phone').value = this.dataset.phone;
        });
    });

});
