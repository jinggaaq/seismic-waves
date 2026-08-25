/* ==========================================
                SHOP PAGE
   ========================================== */

const productGrid = document.getElementById("productGrid");
const pagination = document.getElementById("pagination");

const productsPerPage = 6;

let currentPage = 1;


/* ==========================================
                GET PRODUCTS
   ========================================== */

function getProducts() {

    if (!productGrid) {
        return [];
    }

    return Array.from(
        productGrid.querySelectorAll(".shop-card")
    );

}


/* ==========================================
                PAGINATION
   ========================================== */

function renderProducts() {

    const products = getProducts();

    const start =
        (currentPage - 1) * productsPerPage;

    const end =
        start + productsPerPage;


    products.forEach((product, index) => {

        if (index >= start && index < end) {

            product.style.display = "";

        } else {

            product.style.display = "none";

        }

    });

}


/* ==========================================
                PAGINATION BUTTON
   ========================================== */

function renderPagination() {

    if (!pagination) {
        return;
    }

    const products = getProducts();

    pagination.innerHTML = "";


    const totalPages =
        Math.ceil(
            products.length / productsPerPage
        );


    if (totalPages <= 1) {
        return;
    }


    /* Previous */

    const previousButton =
        document.createElement("button");

    previousButton.innerHTML =
        `<i class="fa-solid fa-angle-left"></i>`;

    previousButton.disabled =
        currentPage === 1;


    previousButton.addEventListener(
        "click",
        () => {

            if (currentPage > 1) {

                currentPage--;

                renderProducts();

                renderPagination();

                window.scrollTo({
                    top: 0,
                    behavior: "smooth"
                });

            }

        }
    );


    pagination.appendChild(
        previousButton
    );


    /* Page Numbers */

    for (
        let page = 1;
        page <= totalPages;
        page++
    ) {

        const pageButton =
            document.createElement("button");

        pageButton.innerText = page;


        if (page === currentPage) {

            pageButton.classList.add("active");

        }


        pageButton.addEventListener(
            "click",
            () => {

                currentPage = page;

                renderProducts();

                renderPagination();

                window.scrollTo({
                    top: 0,
                    behavior: "smooth"
                });

            }
        );


        pagination.appendChild(
            pageButton
        );

    }


    /* Next */

    const nextButton =
        document.createElement("button");

    nextButton.innerHTML =
        `<i class="fa-solid fa-angle-right"></i>`;

    nextButton.disabled =
        currentPage === totalPages;


    nextButton.addEventListener(
        "click",
        () => {

            if (
                currentPage < totalPages
            ) {

                currentPage++;

                renderProducts();

                renderPagination();

                window.scrollTo({
                    top: 0,
                    behavior: "smooth"
                });

            }

        }
    );


    pagination.appendChild(
        nextButton
    );

}


/* ==========================================
                ADD TO CART
   ========================================== */

function activateCart() {

    const buttons =
        document.querySelectorAll(
            ".add-cart"
        );


    buttons.forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const id =
                    Number(button.dataset.id);

                const name =
                    button.dataset.name;

                const price =
                    Number(button.dataset.price);

                const image =
                    button.dataset.image;


                let cart =
                    JSON.parse(
                        localStorage.getItem("cart")
                    ) || [];


                const existing =
                    cart.find(
                        item => item.id === id
                    );


                if (existing) {

                    existing.qty += 1;

                } else {

                    cart.push({

                        id: id,

                        name: name,

                        price: price,

                        image: image,

                        qty: 1

                    });

                }


                localStorage.setItem(
                    "cart",
                    JSON.stringify(cart)
                );


                alert(
                    `${name} berhasil ditambahkan ke cart!`
                );

            }
        );

    });

}


/* ==========================================
                WISHLIST
   ========================================== */

function activateWishlist() {

    const buttons =
        document.querySelectorAll(
            ".wishlist"
        );


    buttons.forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const icon =
                    button.querySelector("i");


                if (!icon) {
                    return;
                }


                icon.classList.toggle(
                    "fa-regular"
                );

                icon.classList.toggle(
                    "fa-solid"
                );

            }
        );

    });

}


/* ==========================================
                INITIALIZE
   ========================================== */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        renderProducts();

        renderPagination();

        activateCart();

        activateWishlist();

    }
);