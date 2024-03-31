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

const currency = function (number) {
    return new Intl.NumberFormat().format(number);
};

// Getting table data usign Ajax

// Pagination
let page_text = document.querySelector(".page-text")
let animation_container_products = document.querySelector(".animations-content_container_products")
let animation_container_logs = document.querySelector(".animations-content_container_logs")

function update_data(page, type) {

    // Show loading animation
    if(type == "products") {
        animation_container_products.style.display = "flex"
    }
    if(type == "logs") {
        animation_container_logs.style.display = "flex"
    }

    $.ajax({
        type: "POST",
        url: "/local-data",
        data: { "page": page },
        //contentType: "application/json;charset=UTF-8",
        //dataType: 'json',
        success: function (result) {

            page_text.innerHTML = "Page " + page;

            if (type == "products") {

                table.innerHTML = "";

                // Update Products Table
                let count = 0
                for (row in result["products"]) {

                    // Si el producto esta publicado

                    if (result["products"][row]["status"] == "publish") {
                        
                        let product_price = 0;

                        if (result["products"][row]["sale_price"] != "") {
                            product_price = currency(result["products"][row]["sale_price"])
                        } else {
                            product_price = currency(result["products"][row]["regular_price"])
                        }

                        let new_row = `
                        <tr>
                            <td><img src="${result["imgs"][result["products"][row]["id"]]}" width='50px' height='50px'></td>
                            <th scope="row">${result["products"][row]["id"]}</th>
                            <td>${result["products"][row]["sku"]}</td>
                            <td>$${product_price}</td>
                            <td>${result["products"][row]["name"]}</td>
                        </tr>`;

                        table.innerHTML += new_row;
                        count++;
                    }
                
                };

                // Pagination state
                counter.innerHTML = `<e>${count}</e> elements <e class="text-hidden_mobile">are displayed</e>`
                if (count >= 100) {
                    $(".forward-icon").removeClass('disabled');
                } else {
                    $(".forward-icon").addClass('disabled');
                }

            }

            if (type == "logs") {

                // Uptade Logs Table

                logs_table.innerHTML = "";

                log_total_qty.innerHTML = result["logs_qty"];
                last_log_date.innerHTML = result["last_log_date"];
                today_log_qty.innerHTML = result["today_log_qty"];

                count = 0;
                for (row in result["logs"]) {

                    let log_products = ``;

                    for (product in result["logs"][row]["products"]) {

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
                        <th scope="row">${count + 1}</th>
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

                $(".show-products_modal_btn").map(function () {

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

        },
        complete: function () {
            if(type == "products") {
                animation_container_products.style.display = "none"
            }

            if(type == "logs") {
                animation_container_logs.style.display = "none"
            }
        }
    });
}

let current_page = 1
update_data(current_page, "products") // The data is loaded (first load)
update_data(current_page, "logs") // The data is loaded (first load)

// Pagination

$('.forward-icon').click(function () {

    if ($(this).hasClass("disabled")) {
        console.log("current page - ", current_page)
    } else {
        $(".back-icon").removeClass('disabled');
        current_page = current_page + 1
        update_data(current_page, "products")
    }
})

$('.back-icon').click(function () {

    if ($(this).hasClass("disabled")) {
        console.log("current page - ", current_page)
    } else {
        current_page = current_page - 1
        update_data(current_page, "products")
        if (current_page == 1) {
            $(".back-icon").addClass('disabled');
        }
    }
})

function update_all_product_prices(update_option = { "option": "2" }) {

    // Se registra la hora en la consola
    // Crear un nuevo objeto Date
    var fechaActual = new Date();

    // Obtener la hora, los minutos y los segundos
    var horas = fechaActual.getHours();
    var minutos = fechaActual.getMinutes();
    var segundos = fechaActual.getSeconds();

    // Formatear la hora para que tenga el formato HH:MM:SS
    var horaActual = horas + ":" + minutos + ":" + segundos;

    // Mostrar la hora actual
    console.log("Actualizando precios, la hora actual es:", horaActual);
    
    // Se actualizan todos los productos

    // Ingram UPDATE
    $.ajax({
        type: "POST",
        url: '/ingram-update',
        data: update_option,
        dataType: 'json',
        beforeSend: function () {
            $('.load-message').removeClass('display-none')
            $('.last-update-message').addClass('display-none')
            $('.success-message').addClass('display-none')
        },
        success: function (data) {
            update_data(current_page, "logs")
        },
        complete: function () {
            // $('.load-message').addClass('display-none')
            $('.success-message').addClass('display-none')
        },
    });
    
    // Intcomex UPDATE
    $.ajax({
        type: "POST",
        url: '/intcomex-update',
        data: update_option,
        dataType: 'json',
        beforeSend: function () {
            $('.load-message').removeClass('display-none')
            $('.last-update-message').addClass('display-none')
            $('.success-message').addClass('display-none')
        },
        success: function (data) {
            update_data(current_page, "logs")
        },
        complete: function () {
            $('.load-message').addClass('display-none')
            $('.success-message').removeClass('display-none')
        },
    });

}

// Se ejecutara esta funcion cada 30 minutos

var timeInterval = 1800000; // 1800000 milisegundos = 30 minutos

// Ejecutar la función AJAX inicialmente
update_all_product_prices();

// Ejecutar la función AJAX periódicamente cada cierto intervalo de tiempo
var intervalID = setInterval(update_all_product_prices, timeInterval);

// Update section

$('.update-button').click(function () {

    let update_option = { "option": "2" }
    let url = "/all-update"
    if ($('.only-ingram').is(':checked')) { update_option = { "option": "0" }; url = "/ingram-update" }
    if ($('.only-intcomex').is(':checked')) { update_option = { "option": "1" }; url = "/intcomex-update" }
    if ($('.all-cells').is(':checked')) { update_option = { "option": "2" }; url = "/all-update" }

    // Si se esta realizando una actualización en especifico
    if (url != "/all-update") {
        
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
                update_data(current_page, "logs")
            },
            complete: function () {
                $('.load-message').addClass('display-none')
                $('.success-message').removeClass('display-none')
            },
        });

    // Si se estan actualizando todos
    } else {

        // Se actualizan todos los precios

        update_all_product_prices()

    }

    
});