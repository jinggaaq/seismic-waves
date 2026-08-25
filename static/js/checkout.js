document.addEventListener('DOMContentLoaded', function () {

    // =========================
    // Shipping option
    // =========================
    const shippingOptions = document.querySelectorAll('.shipping-option');

    shippingOptions.forEach(option => {
        option.addEventListener('click', function () {

            shippingOptions.forEach(o => o.classList.remove('active'));
            this.classList.add('active');

            const radio = this.querySelector('input[type="radio"]');

            if (radio) {
                radio.checked = true;
            }

        });
    });


    // =========================
    // Payment option
    // =========================
    const paymentOptions = document.querySelectorAll('.payment-option');

    paymentOptions.forEach(option => {
        option.addEventListener('click', function () {

            paymentOptions.forEach(o => o.classList.remove('active'));
            this.classList.add('active');

            const radio = this.querySelector('input[type="radio"]');

            if (radio) {
                radio.checked = true;
            }

        });
    });


    // =========================
    // Phone number formatting
    // =========================
    const phoneInput = document.querySelector('input[name="phone"]');

    if (phoneInput) {

        phoneInput.addEventListener('input', function () {

            // Hanya boleh angka
            this.value = this.value.replace(/[^0-9]/g, '');

        });

    }


    // =========================
    // Form validation
    // =========================
    const checkoutForm = document.querySelector('.checkout-form form');
    const placeOrderBtn = document.querySelector('.place-order-btn');

    if (checkoutForm) {

        checkoutForm.addEventListener('submit', function (e) {

            let isValid = true;

            // =========================
            // Required fields
            // =========================
            const requiredFields = [
                'email',
                'full_name',
                'address',
                'city',
                'postal_code',
                'province',
                'phone'
            ];


            requiredFields.forEach(name => {

                const field = checkoutForm.querySelector(
                    `[name="${name}"]`
                );

                if (!field) {
                    return;
                }

                if (field.value.trim() === '') {

                    isValid = false;
                    field.classList.add('input-error');

                } else {

                    field.classList.remove('input-error');

                }

            });


            // =========================
            // Email validation
            // =========================
            const emailField = checkoutForm.querySelector(
                '[name="email"]'
            );

            if (emailField) {

                const emailPattern =
                    /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

                if (
                    emailField.value.trim() === '' ||
                    !emailPattern.test(emailField.value.trim())
                ) {

                    isValid = false;
                    emailField.classList.add('input-error');

                } else {

                    emailField.classList.remove('input-error');

                }

            }


            // =========================
            // Phone validation
            // =========================
            const phoneField = checkoutForm.querySelector(
                '[name="phone"]'
            );

            if (phoneField) {

                const phoneValue = phoneField.value.trim();

                if (
                    phoneValue === '' ||
                    phoneValue.length < 10
                ) {

                    isValid = false;
                    phoneField.classList.add('input-error');

                } else {

                    phoneField.classList.remove('input-error');

                }

            }


            // =========================
            // Postal code validation
            // =========================
            const postalField = checkoutForm.querySelector(
                '[name="postal_code"]'
            );

            if (postalField) {

                const postalValue = postalField.value.trim();

                if (
                    postalValue === '' ||
                    !/^[0-9]+$/.test(postalValue)
                ) {

                    isValid = false;
                    postalField.classList.add('input-error');

                } else {

                    postalField.classList.remove('input-error');

                }

            }


            // =========================
            // Payment method
            // =========================
            const paymentMethod =
                checkoutForm.querySelector(
                    'input[name="payment_method"]:checked'
                );

            if (!paymentMethod) {

                isValid = false;

            }


            // =========================
            // Validation result
            // =========================
            if (!isValid) {

                e.preventDefault();

                alert(
                    'Please complete all required fields correctly.'
                );

                return;

            }


            // =========================
            // Button loading state
            // =========================
            if (placeOrderBtn) {

                placeOrderBtn.disabled = true;

                placeOrderBtn.innerHTML = `
                    <i class="fa-solid fa-spinner fa-spin"></i>
                    Processing...
                `;

            }

        });

    }


    // =========================
    // Remove error state
    // =========================
    const inputs = document.querySelectorAll(
        '.form-group input, .form-group select'
    );

    inputs.forEach(input => {

        input.addEventListener('input', function () {

            this.classList.remove('input-error');

        });

        input.addEventListener('change', function () {

            this.classList.remove('input-error');

        });

    });


    // =========================
    // Smooth focus effect
    // =========================
    inputs.forEach(input => {

        input.addEventListener('focus', function () {

            this.parentElement.classList.add('focused');

        });

        input.addEventListener('blur', function () {

            this.parentElement.classList.remove('focused');

        });

    });

});