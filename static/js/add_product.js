
/* Se cargan los elementos para añadir un producto */

const add_prod_button = $('.add-prod-button_modal');
const add_prod_modal = $('.add-prod-container')

// Si se da click en añadir producto se muestra el modal
$(add_prod_button).click(function () {
    $('.add-prod-container').removeClass('display-none');
})

// Si se da click en cerrar se oculta el modal
$(add_prod_modal).find(".close-modal_button").click(function () {
    $('.add-prod-container').addClass('display-none');
});

// Si se da click en añadir producto dentro del modal
$(".add-prod-button").click(function () {

    // Se obtienen todos los valores del formulario en el modal
    let prod_sku = $(".prod-sku-input").val();
    let prod_pn = $(".prod-pn-input").val();
    let category = $(".category-select").val();
    let provider = $(".provider-select").val();
    
    // URL para añadir un nuevo producto
    let url = "/add-product"

    // Si no hay datos vacios
    if (prod_sku != "" && category != "" && provider != "") {
        
        // Consulta AJAX de tipo POST
        $.ajax({
            type: "POST",
            url: url,
            data: {
                "prod_sku": prod_sku,
                "prod_pn": prod_pn,
                "category": category,
                "provider": provider
            },
            dataType: 'json',
            success: function (data) {
                
                // Si la consulta se realizo correctamente
                $(".add-prod-fill-message").addClass("display-none");
                $(".add-prod-error-message").addClass("display-none");
                $(".first-message").addClass("display-none");
                $(".prod-success-message").removeClass("display-none");

                // Se actualiza la tabla de registros
                update_data(1);
            },
            error: function () {

                // Si la consulta no se pudo realizar, lanzar un error
                $(".add-prod-fill-message").addClass("display-none");
                $(".prod-success-message").addClass("display-none");
                $(".first-message").addClass("display-none");
                $(".add-prod-error-message").removeClass("display-none");
            }
        });

    } else {

        // Si no se llenan todos los campos correctamente
        $(".add-prod-error-message").addClass("display-none");
        $(".prod-success-message").addClass("display-none");
        $(".first-message").addClass("display-none");
        $(".add-prod-fill-message").removeClass("display-none")
    }

});