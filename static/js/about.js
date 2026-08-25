/* ==========================================
        ABOUT PAGE ANIMATION
========================================== */

document.addEventListener("DOMContentLoaded", function(){

    /* ==========================================
            PAGE LOAD ANIMATION
    ========================================== */

    document.body.classList.add("page-loaded");


    /* ==========================================
            PAGE TRANSITION
    ========================================== */

    const links = document.querySelectorAll("a");

    links.forEach(link => {

        link.addEventListener("click", function(e){

            const href = this.getAttribute("href");


            /* Abaikan link kosong */

            if(!href || href === "#"){
                return;
            }


            /* Abaikan link eksternal */

            if(
                href.startsWith("http") ||
                href.startsWith("mailto:") ||
                href.startsWith("tel:")
            ){
                return;
            }


            /* Abaikan link yang membuka tab baru */

            if(this.target === "_blank"){
                return;
            }


            e.preventDefault();


            /* Animasi keluar */

            document.body.classList.remove("page-loaded");

            document.body.classList.add("page-exit");


            /* Pindah halaman setelah animasi */

            setTimeout(function(){

                window.location.href = href;

            }, 500);

        });

    });

});