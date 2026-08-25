document.addEventListener('DOMContentLoaded', function () {

    const qtyForms = document.querySelectorAll('.qty-form');

    qtyForms.forEach(form => {

        const minusBtn = form.querySelector('.qty-minus');
        const plusBtn = form.querySelector('.qty-plus');
        const input = form.querySelector('input[name="jumlah"]');

        // tombol minus
        minusBtn.addEventListener('click', function (e) {
            e.preventDefault();

            let qty = parseInt(input.value) || 1;

            if (qty > 1) {
                input.value = qty - 1;
                form.requestSubmit(); // submit form
            }
        });

        // tombol plus
        plusBtn.addEventListener('click', function (e) {
            e.preventDefault();

            let qty = parseInt(input.value) || 1;
            const stock = parseInt(this.dataset.stock) || 999;

            if (qty < stock) {
                input.value = qty + 1;
                form.requestSubmit(); // submit form
            } else {
                alert('Stok tidak mencukupi');
            }
        });

    });

});



