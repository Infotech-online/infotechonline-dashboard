
// Se necesita la libreria Swiper para ejecutar este codigo

const progressCircle = document.querySelector(".autoplay-progress svg");
const progressContent = document.querySelector(".autoplay-progress span");
var swiper = new Swiper(".mySwiper", {
	spaceBetween: 30,
	centeredSlides: true,
	autoplay: {
		delay: 3500,
		disableOnInteraction: false
	},
	loop: true,
	pagination: {
		el: ".swiper-pagination",
		clickable: true
	},
	navigation: {
		nextEl: ".swiper-button-next",
		prevEl: ".swiper-button-prev"
	},
	on: {
		autoplayTimeLeft(s, time, progress) {
			progressCircle.style.setProperty("--progress", 1 - progress);
			progressContent.textContent = `${Math.ceil(time / 1000)}s`;
		}
	}
});