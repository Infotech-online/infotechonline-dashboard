// Elements

// Products
let table = document.querySelector(".table-body")
let counter = document.querySelector(".elements-loaded-text")
let log_total_qty = document.querySelector(".log-total-qty")
let last_log_date = document.querySelector(".last-log-date")
let today_log_qty = document.querySelector(".today-log-qty")

// Logs
let logs_table = document.querySelector(".logs-table .table-body")

// Number to currency format

const currency = function(number){
    return new Intl.NumberFormat().format(number);
};

// Getting table data usign Ajax

// Pagination
let page_text = document.querySelector(".page-text")

function update_data(page) {

    table.innerHTML = "";
    logs_table.innerHTML = "";

    $.ajax({
        type: "POST",
        url: "/local-data",
        data: {"page": page},
        //contentType: "application/json;charset=UTF-8",
        //dataType: 'json',
        success: function (result) {
            
            log_total_qty.innerHTML = result["logs_qty"];
            last_log_date.innerHTML = result["last_log_date"];
            today_log_qty.innerHTML = result["today_log_qty"];
            page_text.innerHTML = "Page " + page;
            
            // Products
            let count = 0
            for(row in result["products"]) {
                
                let new_row = `
                <tr>
                    <th scope="row">${result["products"][row]["id"]}</th>
                    <td>${result["products"][row]["sku"]}</td>
                    <td>${currency(result["products"][row]["regular_price"])}</td>
                    <td>${result["products"][row]["name"]}</td>
                </tr>`;
    
                table.innerHTML += new_row;
                count++;
            };
            
            // Pagination state
            counter.innerHTML = `<e>${count}</e> elements <e class="text-hidden_mobile">are displayed</e>`
            if(count >= 100) {
                $( ".forward-icon" ).removeClass('disabled');
            } else {
                $( ".forward-icon" ).addClass('disabled');
            }

            // Logs
            
            count = 0;
            for(row in result["logs"]) {

                let log_products = `
                
                `;

                for(product in result["logs"][row]["products"]) {

                    product_info = result["logs"][row]["products"][product];

                    let log_product = `
                        <div class="log-product">
                            <div class="image-container"><img src="${result["imgs"][product_info["id"]]}"></div>
                            <div class="product-info-container">
                                <span class="product-sku">${product_info["sku"]} - ${product_info["id"]}</span>
                                <div class="price-container">
                                    <div><span class="stock-status">${product_info["stock"]}</span></div>
                                    <div><span class="last-price_title">Last price:</span> <e class="last-price_qty">${currency(product_info["past_price"])}</e></div>
                                    <div><span class="curr-price_title">Current price:</span> <e class="curr-price_qty">${currency(product_info["regular_price"])}</e></div>
                                </div>
                            </div>
                        </div>
                    `;

                    log_products += log_product;
                }

                let log_type = result["logs"][row]["type"]
                if (log_type == "Update") {
                    log_type = "<span class='log-type_message log-type_message_update'>Update</span>";
                } else if (log_type == "Add") {
                    log_type = "<span class='log-type_message log-type_message_add'>Add</span>";
                } else {
                    log_type = "<span class='log-type_message log-type_message_update'>Update</span>";
                }

                let new_row = `
                <tr>
                    <th scope="row">${count+1}</th>
                    <td>${result["logs"][row]["date"]}</td>
                    <td>${result["logs"][row]["qty"]}</td>
                    <td>${log_type}</td>
                    <td class="show-products_action-btn" style="text-decoration: underline;">
                        <span class="show-products_modal_btn">Ver productos</span>
                        <div class="upd-prod-container display-none">
                            <div class="buttons-container"><span class="close-modal_button"><ion-icon name="close-outline"></ion-icon></span></div>
                            <div class="upd-prod-content">
                                ${log_products}
                            </div>
                        </div>
                    </td>
                </tr>`;
    
                logs_table.innerHTML += new_row;
                count++;
            }

            $(".show-products_modal_btn").map(function() {

                let parent = $(this).parent();
                let modal = parent.children(".upd-prod-container");

                $(this).click(function () {
                    // Display the modal
                    $(modal).removeClass("display-none");
                });

                // Add close function
                let buttons_container = modal.children(".buttons-container");
                let close_btn = buttons_container.children(".close-modal_button");
                $(close_btn).click(function () {
                    $(modal).addClass("display-none");
                });

            });
        }
    });
}

let current_page = 1
update_data(current_page) // The data is loaded (first load)

// Pagination

$('.forward-icon').click(function () {

    if($(this).hasClass("disabled")) {
        console.log("current page - ", current_page)
    } else {
        $(".back-icon").removeClass('disabled');
        current_page = current_page + 1
        update_data(current_page)
    }
})

$('.back-icon').click(function () {
    
    if($(this).hasClass("disabled")) {
        console.log("current page - ", current_page)
    } else {
        current_page = current_page - 1
        update_data(current_page)
        if(current_page == 1) {
            $(".back-icon").addClass('disabled'); 
        }
    }
})

// Update section

$('.update-button').click(function () {
    
    let update_option = {"option": "2"}
    let url = "/all-update"
    if($('.only-ingram').is(':checked')) { update_option = {"option": "0"}; url="/ingram-update"}
    if($('.only-intcomex').is(':checked')) { update_option = {"option": "1"}; url="/intcomex-update"}
    if($('.all-cells').is(':checked')) { update_option = {"option": "2"}; url="/all-update"}

    $.ajax({
        type: "POST",
        url: url,
        data: update_option,
        dataType: 'json',
        beforeSend: function () {
            $('.load-message').removeClass('display-none')
            $('.last-update-message').addClass('display-none')
            $('.success-message').addClass('display-none')
        },
        success: function (data) {
        },
        complete: function () {
            $('.load-message').addClass('display-none')
            $('.success-message').removeClass('display-none')
            update_data(current_page)
        },
    });
});
