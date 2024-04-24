function copy_filter_menu_content() {

    jQuery(document).ready(function($) {

        let filter_menu = document.querySelector(".shop-filter-content_container")
        let hidden_filter_menu = document.querySelector(".hidden-menu_content")

        console.log(hidden_filter_menu)
        console.log(filter_menu)
        hidden_filter_menu.innerHTML = filter_menu.innerHTML

    })

}

// copy_filter_menu_content()

document.addEventListener("DOMContentLoaded", function () {
    // Obtener el elemento
    var elemento = document.querySelector(".hidden-menu-content_container");

    // Obtener el ancho del elemento
    var anchoElemento = elemento.offsetWidth;

    // Aplicar el left negativo
    elemento.style.left = "-" + anchoElemento + "px";
});

let filter_button = document.querySelector(".filter-menu_button")

filter_button.addEventListener("click", function () {

    // Obtener el elemento
    var elemento = document.querySelector(".hidden-menu-content_container");

    // Obtener el ancho del elemento
    var anchoElemento = elemento.offsetWidth;

    anime({
        targets: '.hidden-menu-content_container',
        translateX: anchoElemento,
        duration: 300,
        easing: 'easeInOutQuad'
    });

})

let close_button = document.querySelector(".close_button")

close_button.addEventListener("click", function() {

    // Obtener el elemento
    var elemento = document.querySelector(".hidden-menu-content_container");

    // Obtener el ancho del elemento
    var anchoElemento = elemento.offsetWidth;

    anime({
        targets: '.hidden-menu-content_container',
        translateX: -anchoElemento,
        duration: 300,
        easing: 'easeInOutQuad'
    });

})


