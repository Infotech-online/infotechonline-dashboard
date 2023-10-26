
/* Add Product Modal */

const add_prod_button = $('.add-prod-button_modal');
const add_prod_modal = $('.add-prod-container')

$(add_prod_button).click(function () {
    $('.add-prod-container').removeClass('display-none');
})

$(add_prod_modal).find(".close-modal_button").click(function () {
    $('.add-prod-container').addClass('display-none');
});

$(".add-prod-button").click(function () {

    let prod_sku = $(".prod-sku-input").val();
    let prod_pn = $(".prod-pn-input").val();
    let category = $(".category-select").val();
    let provider = $(".provider-select").val();

    let url = "/add-product"

    if (prod_sku != "" && category != "" && provider != "") {
        
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
                $(".add-prod-fill-message").addClass("display-none");
                $(".add-prod-error-message").addClass("display-none");
                $(".first-message").addClass("display-none");
                $(".prod-success-message").removeClass("display-none");
                update_data(1);
            },
            error: function () {
                $(".add-prod-fill-message").addClass("display-none");
                $(".prod-success-message").addClass("display-none");
                $(".first-message").addClass("display-none");
                $(".add-prod-error-message").removeClass("display-none");
            }
        });

    } else {
        $(".add-prod-error-message").addClass("display-none");
        $(".prod-success-message").addClass("display-none");
        $(".first-message").addClass("display-none");
        $(".add-prod-fill-message").removeClass("display-none")
    }

});