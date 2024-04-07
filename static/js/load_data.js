// Elements

// Se cargan los elementos del DOM
let table = document.querySelector(".table-body")
let counter = document.querySelector(".elements-loaded-text")
let log_total_qty = document.querySelector(".log-total-qty")
let last_log_date = document.querySelector(".last-log-date")
let today_log_qty = document.querySelector(".today-log-qty")

// Tabla de registros o actualizaciones
let logs_table = document.querySelector(".logs-table .table-body")

// Formato de moneda (Pesos colombianos)

const currency = function (number) {
    return new Intl.NumberFormat().format(number);
};

// Pagination
let page_text = document.querySelector(".page-text")

// Contenedores de animación de carga
let animation_container_products = document.querySelector(".animations-content_container_products")
let animation_container_logs = document.querySelector(".animations-content_container_logs")

// Función que actualiza los datos del DOM cuando se hacen peticiones al servidor
function update_data(page, type) {

    // Mostrar animaciónes de carga
    if(type == "products") {
        animation_container_products.style.display = "flex"
    }
    if(type == "logs") {
        animation_container_logs.style.display = "flex"
    }
    
    // Petición AJAX de tipo POST
    // A la URL de /local-data
    $.ajax({
        type: "POST",
        url: "/local-data",
        data: { "page": page },
        //contentType: "application/json;charset=UTF-8",
        //dataType: 'json',

        success: function (result) {

            // Si la petición se realizó correctamente
            
            page_text.innerHTML = "Page " + page;
            
            // Si se actualizó la tabla de productos de la tienda
            if (type == "products") {
                
                // Limpiar el contenedor de la tabla
                table.innerHTML = "";

                // Actualizar los productos
                // La variable "count" almacena la cantidad de productos dentro de la pagina
                let count = 0
                // Por cada fila de productos en el resultado de la petición
                for (row in result["products"]) {

                    // Si el producto esta publicado en la tienda
                    if (result["products"][row]["status"] == "publish") {
                        
                        let product_price = 0;
                        
                        // Si el producto esta en oferta
                        if (result["products"][row]["sale_price"] != "") {
                            product_price = currency(result["products"][row]["sale_price"])
                        } else {
                            // Si el producto no esta en oferta
                            product_price = currency(result["products"][row]["regular_price"])
                        }
                        
                        // Se crea una nueva fila de la tabla
                        let new_row = `
                        <tr>
                            <td><img src="${result["imgs"][result["products"][row]["id"]]}" width='50px' height='50px'></td>
                            <th scope="row">${result["products"][row]["id"]}</th>
                            <td>${result["products"][row]["sku"]}</td>
                            <td>$${product_price}</td>
                            <td>${result["products"][row]["name"]}</td>
                        </tr>`;
                        
                        // Se añade la nueva fila a la tabla
                        table.innerHTML += new_row;
                        // Se suma 1 a la cantidad de productos
                        count++;
                    }
                
                };

                // Se cambia el estado de la paginación (la cantidad de productos)
                counter.innerHTML = `<e>${count}</e> elements <e class="text-hidden_mobile">are displayed</e>`;

                // Si la cantidad de productos es mayor o igual a 100, se activa el boton de la siguiente página
                if (count >= 100) {
                    $(".forward-icon").removeClass('disabled');
                } else {
                    // Si no, se deshabilita
                    $(".forward-icon").addClass('disabled');
                }

            }

            // Si se estan actualizando los registros o Logs
            if (type == "logs") {

                // Se limpia la tabla de registros
                logs_table.innerHTML = "";

                // Se actualizan los valores de las actualizaciones totales
                log_total_qty.innerHTML = result["logs_qty"];
                last_log_date.innerHTML = result["last_log_date"];
                today_log_qty.innerHTML = result["today_log_qty"];
                
                // La variable "count" mide la cantidad de registros
                count = 0;
                // Por cada fila dentro de los registros
                for (row in result["logs"]) {

                    // Esta variable almacena los nuevos elementos que se añadiran en los detalles de cada registro
                    let log_products = ``;

                    // Por cada producto dentro de un registro
                    for (product in result["logs"][row]["products"]) {

                        // Se obtiene la información del producto
                        product_info = result["logs"][row]["products"][product];

                        // Estructura del producto dentro del DOM
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

                        // Se concatena a los demas productos
                        log_products += log_product;
                    }
                    
                    // Obtener el tipo de registro o actualización
                    let log_type = result["logs"][row]["type"]
                    
                    // Si es de tipo "update"
                    if (log_type == "Update") {
                        log_type = "<span class='log-type_message log-type_message_update'>Update</span>";
                    
                    // Si es de tipo "Add"
                    } else if (log_type == "Add") {
                        log_type = "<span class='log-type_message log-type_message_add'>Add</span>";

                    } else {
                        log_type = "<span class='log-type_message log-type_message_update'>Update</span>";
                    }

                    // Se crea una nueva fila dentro para la tabla de registros
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
                    
                    // Se añade una nueva fila dentro de la tabla de registros (DOM)
                    logs_table.innerHTML += new_row;
                    // Se suma 1 a la cantidad de registros
                    count++;
                }

                // Se da funcionalidad a cada modal dentro de los registros
                $(".show-products_modal_btn").map(function () {

                    // Se obtiene el contenedor padre del modal (registro)
                    let parent = $(this).parent();
                    // Se obtiene el modal
                    let modal = parent.children(".upd-prod-container");

                    // Si se da click en el boton de "ver mas detalles"
                    $(this).click(function () {
                        // Se muestra el modal
                        $(modal).removeClass("display-none");
                    });

                    // Se añade la funcion de cerrar el modal despues de abrirlo
                    let buttons_container = modal.children(".buttons-container"); // Obtener botones
                    let close_btn = buttons_container.children(".close-modal_button"); // Obtener el boton de cerrar

                    // Si se da click en el boton de cerrar
                    $(close_btn).click(function () {

                        // Se oculta el modal
                        $(modal).addClass("display-none");
                    });

                });

            }

        },

        // Cuando se finalia o completa la petición
        complete: function () {

            // Se ocultan todas las animaciones
            if(type == "products") {
                animation_container_products.style.display = "none"
            }

            if(type == "logs") {
                animation_container_logs.style.display = "none"
            }
        }
    });
}

// Cuando la pagina se inicia por primera vez se ejecuta la funcion de actualizar datos
let current_page = 1
update_data(current_page, "products") // The data is loaded (first load)
update_data(current_page, "logs") // The data is loaded (first load)

// Botones de la paginación de las tablas de contenido

// Boton de avanzar hacia adelante
$('.forward-icon').click(function () {

    if ($(this).hasClass("disabled")) {
        console.log("current page - ", current_page)
    } else {
        $(".back-icon").removeClass('disabled');
        current_page = current_page + 1
        update_data(current_page, "products")
    }
})

// Boton de avanzar hacia atras
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

// Se actualizan todos los productos de todos los proveedores
function update_all_product_prices(update_option = { "option": "2" }) {

    /*
    Esta función se encarga de actualizar todos los precios, primero actualiza los precios
    de Ingram y luego de finalizar esta consulta se actualizan los de Intcomex
    */

    // Se registra la hora en la consola
    var fecha_actual = new Date();

    // Obtener la hora, los minutos y los segundos
    var horas = fecha_actual.getHours();
    var minutos = fecha_actual.getMinutes();
    var segundos = fecha_actual.getSeconds();

    // Formatear la hora para que tenga el formato HH:MM:SS
    var hora_actual = horas + ":" + minutos + ":" + segundos;

    // Mostrar la hora actual
    console.log("Actualizando precios, la hora actual es:", hora_actual);

    // Petición AJAX de tipo POST hacia la URL /ingram-update
    $.ajax({
        type: "POST",
        url: '/ingram-update',
        data: update_option,
        dataType: 'json',

        // Antes de enviar la petición se muestra el mensaje de "cargando..."
        beforeSend: function () {
            $('.load-message').removeClass('display-none')
            $('.last-update-message').addClass('display-none')
            $('.success-message').addClass('display-none')
        },

        // Si la petición se ejecuta exitosamente
        success: function (data) {
            
            // Se realiza una actualización a los registros
            update_data(current_page, "logs")

            // Actualizar los precios de Intcomex al finalizar la actualización de Ingram
            // Petición AJAX de tipo POST hacia la URL /intcomex-update
            $.ajax({
                type: "POST",
                url: '/intcomex-update',
                data: update_option,
                dataType: 'json',

                // Antes de enviar la petición se muestra el mensaje de "cargando..."
                beforeSend: function () {
                    $('.load-message').removeClass('display-none')
                    $('.last-update-message').addClass('display-none')
                    $('.success-message').addClass('display-none')
                },
                // Si la petición se ejecuta exitosamente
                success: function (data) {
                    // Se realiza una actualización a los registros
                    update_data(current_page, "logs")
                },
                complete: function () {
                    // Cuando se completa la petición se añade el mensaje de "completado con exito"
                    $('.load-message').addClass('display-none')
                    $('.success-message').removeClass('display-none')
                },
            });

        },
        complete: function () {
            // Cuando se completa la petición se añade el mensaje de "completado con exito"
            $('.success-message').addClass('display-none')
        },
    });

}

// Se ejecutara esta funcion cada 30 minutos

// var timeInterval = 1800000; // 1800000 milisegundos = 30 minutos

// Ejecutar la función AJAX inicialmente
// update_all_product_prices();

// Ejecutar la función AJAX periódicamente cada cierto intervalo de tiempo
// var intervalID = setInterval(update_all_product_prices, timeInterval);


// Al precionar el boton de actualizar

$('.update-button').click(function () {

    // Se obtiene la opción elegida por el usuario
    let update_option = { "option": "2" }
    let url = "/all-update"
    if ($('.only-ingram').is(':checked')) { update_option = { "option": "0" }; url = "/ingram-update" }
    if ($('.only-intcomex').is(':checked')) { update_option = { "option": "1" }; url = "/intcomex-update" }
    if ($('.all-cells').is(':checked')) { update_option = { "option": "2" }; url = "/all-update" }

    // Si se esta realizando una actualización en especifico (Ingram o Intcomex)
    if (url != "/all-update") {
        
        // Petición AJAX de tipo POST
        $.ajax({
            type: "POST",
            url: url,
            data: update_option,
            dataType: 'json',

            // Antes de enviar la petición se muestra el mensaje de "cargando..."
            beforeSend: function () {
                $('.load-message').removeClass('display-none')
                $('.last-update-message').addClass('display-none')
                $('.success-message').addClass('display-none')
            },
            // Si la petición se ejecuta exitosamente
            success: function (data) {
                // Se realiza una actualización a los registros
                update_data(current_page, "logs")
            },
            // Cuando se completa la petición se añade el mensaje de "completado con exito"
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