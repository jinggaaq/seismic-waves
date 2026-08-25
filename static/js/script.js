
/* ==========================================
            HERO SLIDER
========================================== */

const heroTrack = document.querySelector(".hero-track");
const slides = document.querySelectorAll(".hero-slide");
const indicators = document.querySelectorAll(".indicator");

const nextBtn = document.querySelector(".hero-next");
const prevBtn = document.querySelector(".hero-prev");

let currentSlide = 0;
let autoSlide;

/* ==========================================
            UPDATE SLIDER
========================================== */

function updateSlider() {

    heroTrack.style.transform =
        `translateX(-${currentSlide * 100}%)`;

    indicators.forEach((dot) => {

        dot.classList.remove("active");

    });

    indicators[currentSlide].classList.add("active");

}

/* ==========================================
            NEXT
========================================== */

function nextSlide() {

    currentSlide++;

    if (currentSlide >= slides.length) {

        currentSlide = 0;

    }

    updateSlider();

}

/* ==========================================
            PREVIOUS
========================================== */

function prevSlide() {

    currentSlide--;

    if (currentSlide < 0) {

        currentSlide = slides.length - 1;

    }

    updateSlider();

}

/* ==========================================
            AUTO SLIDE
========================================== */

function startSlider() {

    clearInterval(autoSlide);

    autoSlide = setInterval(() => {

        nextSlide();

    }, 5000);

}

/* ==========================================
            BUTTON
========================================== */

nextBtn.addEventListener("click", () => {

    nextSlide();

    startSlider();

});

prevBtn.addEventListener("click", () => {

    prevSlide();

    startSlider();

});

/* ==========================================
            INDICATOR
========================================== */

indicators.forEach((dot, index) => {

    dot.addEventListener("click", () => {

        currentSlide = index;

        updateSlider();

        startSlider();

    });

});

/* ==========================================
            MOBILE SWIPE
========================================== */

let startX = 0;
let endX = 0;

const hero = document.querySelector(".hero");

hero.addEventListener("touchstart", (e) => {

    startX = e.changedTouches[0].screenX;

});

hero.addEventListener("touchend", (e) => {

    endX = e.changedTouches[0].screenX;

    if (startX - endX > 60) {

        nextSlide();

        startSlider();

    }

    if (endX - startX > 60) {

        prevSlide();

        startSlider();

    }

});

/* ==========================================
        SCROLL REVEAL ANIMATION
========================================== */

const reveals = document.querySelectorAll(".reveal");

function revealElements() {

    const trigger = window.innerHeight * 0.85;

    reveals.forEach((element) => {

        const top = element.getBoundingClientRect().top;

        if (top < trigger) {

            element.classList.add("active");

        }

    });

}

window.addEventListener("scroll", revealElements);

window.addEventListener("load", revealElements);

/* ==========================================
            START
========================================== */

updateSlider();

startSlider();

revealElements();

