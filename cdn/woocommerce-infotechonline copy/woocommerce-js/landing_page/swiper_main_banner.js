var swiper = new Swiper(".swiper_main_banner", {
    loop: true,
    autoplay: {
        delay: 5000,
        disableOnInteraction: false,
    },
    pagination: {
        el: ".swiper-main-banner-pagination",
        clickable: true,
    },
    navigation: {
        nextEl: ".swiper-main-banner-button-next",
        prevEl: ".swiper-main-banner-button-prev",
    }
});