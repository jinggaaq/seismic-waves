// ==========================================
// Detail produk - Seismic Waves
// ==========================================

document.addEventListener('DOMContentLoaded', function () {

    // ==========================================
    // Gallery thumbnail
    // ==========================================

    const mainImage = document.getElementById('mainImage');
    const thumbs = document.querySelectorAll('.thumb');

    thumbs.forEach(function (thumb) {
        thumb.addEventListener('click', function () {

            if (mainImage) {
                mainImage.src = this.src;
            }

            thumbs.forEach(function (t) {
                t.classList.remove('active');
            });

            this.classList.add('active');
        });
    });

    // ==========================================
    // Size selection
    // ==========================================

    const sizeButtons = document.querySelectorAll('.size-btn');
    const selectedSize = document.getElementById('selectedSize');

    sizeButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {

            sizeButtons.forEach(function (b) {
                b.classList.remove('active');
            });

            this.classList.add('active');

            if (selectedSize) {
                selectedSize.value = this.dataset.size;
            }
        });
    });

    // ==========================================
    // Quantity
    // ==========================================

    const qtyInput = document.getElementById('qty');
    const hiddenQty = document.getElementById('selectedQty');
    const plusBtn = document.getElementById('plusBtn');
    const minusBtn = document.getElementById('minusBtn');

    // Ambil stok dari tombol plus
    const maxStock = parseInt(
        plusBtn ? plusBtn.dataset.stock : '1',
        10
    ) || 1;

    function updateQty(value) {

        if (!qtyInput || !hiddenQty) return;

        qtyInput.value = value;
        hiddenQty.value = value;
    }

    if (plusBtn) {
        plusBtn.addEventListener('click', function () {

            let current = parseInt(qtyInput.value, 10);

            if (current < maxStock) {
                updateQty(current + 1);
            }
        });
    }

    if (minusBtn) {
        minusBtn.addEventListener('click', function () {

            let current = parseInt(qtyInput.value, 10);

            if (current > 1) {
                updateQty(current - 1);
            }
        });
    }

    // ==========================================
// BUY NOW
// ==========================================

const buyNowBtn = document.getElementById('buyNowBtn');
const buyNowForm = document.getElementById('buyNowForm');

const buyNowSize = document.getElementById('buyNowSize');
const buyNowQty = document.getElementById('buyNowQty');

if (buyNowBtn && buyNowForm) {

    buyNowBtn.addEventListener('click', function () {

        // Ambil ukuran yang sedang dipilih
        if (selectedSize && buyNowSize) {
            buyNowSize.value = selectedSize.value;
        }

        // Ambil jumlah yang sedang dipilih
        if (hiddenQty && buyNowQty) {
            buyNowQty.value = hiddenQty.value;
        }

        // Kirim form Buy Now
        buyNowForm.submit();
    });

}

    // ==========================================
    // Add to Cart validation
    // ==========================================

    const form = document.getElementById('addToCartForm');

    if (form) {
        form.addEventListener('submit', function (e) {

            const qty = parseInt(hiddenQty.value, 10);

            if (qty < 1) {
                e.preventDefault();
                alert('Jumlah minimal 1 produk.');
                updateQty(1);
                return;
            }

            if (qty > maxStock) {
                e.preventDefault();
                alert('Jumlah melebihi stok yang tersedia.');
                updateQty(maxStock);
                return;
            }

            if (!selectedSize.value) {
                e.preventDefault();
                alert('Silakan pilih ukuran terlebih dahulu.');
                return;
            }
        });
    }

});