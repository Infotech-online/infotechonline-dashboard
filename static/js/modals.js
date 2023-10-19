
/* Add Product Modal */

const add_prod_button = $('.add-prod-button_modal');
const add_prod_modal = $('.add-prod-container')

$(add_prod_button).click(function () {
    $('.add-prod-container').removeClass('display-none');
})

$(add_prod_modal).find(".close-modal_button").click(function () {
    $('.add-prod-container').addClass('display-none');
});