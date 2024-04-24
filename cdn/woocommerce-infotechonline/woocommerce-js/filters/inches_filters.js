

// En la primera carga de la pagina los valores de las pulgadas seran las de los productos
function set_default_inches_filter_values(action) {

    jQuery(document).ready(function($) {

        if (localStorage.getItem('category_') == 'pantallas' || localStorage.getItem('category_') == 'televisores' || localStorage.getItem('category_') == 'monitores' || localStorage.getItem('category_') == 'monitores-industriales') {

            let selected_brands = [];
            let brands_  = localStorage.getItem('brands_') // Se obtienen las marcas de local storage

            // Si local storage no esta vacio
            if (brands_ != "" && brands_ != null && brands_ != undefined) {
                // Local storage devuelve una string separado por comas de las marcas
                selected_brands = brands_.split(','); // Se convierte en array el string (separado por comas)
            }

            var selected_brands_parsed = JSON.stringify(selected_brands);

            data = {
                "action": "get_all_inches",
                'current_category': localStorage.getItem('category_'),
    			'brand_list': selected_brands_parsed
            }

            var ajaxurl = ajax_object.ajax_url;

            $.post(ajaxurl, data, function(response) {


            }).done(function(response) { // Si la consulta fue realizada con exito

                let response_parsed = JSON.parse(response);
                console.log(response_parsed)
                let min_value = response_parsed[0]
                let max_value = response_parsed[1]

                console.log(min_value, max_value)

                localStorage.setItem('min-inches-default_', min_value) // Pulgadas minimas
                localStorage.setItem('max-inches-default_', max_value) // Pulgadas maximas

                if (action == 'set_values') {

                    set_inches_tags_filter(response_parsed[2])

                    // Se guardan los valores de las pulgadas en el local storage
                    localStorage.setItem('min-inches_', min_value) // Pulgadas minimas
                    localStorage.setItem('max-inches_', max_value) // Pulgadas maximas

                    let min_inches_input = document.querySelector('.min-inches_input');
                    let max_inches_input = document.querySelector('.max-inches_input');

                    min_inches_input.value = min_value
                    max_inches_input.value = max_value

                    load_products()

                }

            })

        }
    })

}

// Cuando la pagina se inicia por primera vez
set_default_inches_filter_values('set_values')


// Cuando las inputs de MIN y MAX cambien se cambia el valor en local storage
function get_inches_filter_values(inches_values_list) {

    // Si el valor minimo es mayor al maximo y el maximo es menor al minimo

    let min_inches_input = document.querySelector('.min-inches_input');
    let max_inches_input = document.querySelector('.max-inches_input');

    // Cuando la input de min-inches cambie de valor (se escriba dentro de la input)
    min_inches_input.addEventListener("input", function() {

        // Valores iniciales de las pulgadas en la categoria
        // get_default_inches_filter_values();
        let max_value_default = localStorage.getItem('max-inches-default_')
        let min_value_default = localStorage.getItem('min-inches-default_')

        // Current inches value
        let max_value = localStorage.getItem('max-inches_')
        let min_value = localStorage.getItem('min-inches_')

        timeoutId = setTimeout(function() {

            // Si el valor maximo no es menor al default o no es mayor al maximo default o no es mayor min-inches a max-inches
            if (!(parseInt(min_inches_input.value) < parseInt(min_value_default) || parseInt(min_inches_input.value) > parseInt(max_value_default) || parseInt(min_inches_input.value) > parseInt(max_inches_input.value))) {
                localStorage.setItem('min-inches_', min_inches_input.value) // Pulgadas minimas
                load_products()
            } else {
                min_inches_input.value = min_value_default
                localStorage.setItem('min-inches_', min_value_default)
                load_products()
            }

            // Logica cuando se selecciona una etiqueta de pulgadas
            select_inches_tags(inches_values_list)

        }, 1000);

    });

    // Cuando la input de max-inches cambie de valor (se escriba dentro de la input)
    max_inches_input.addEventListener("input", function() {

        // Valores iniciales de las pulgadas en la categoria
        // get_default_inches_filter_values();
        let max_value_default = localStorage.getItem('max-inches-default_')
        let min_value_default = localStorage.getItem('min-inches-default_')

        // Current inches value
        let max_value = localStorage.getItem('max-inches_')
        let min_value = localStorage.getItem('min-inches_')

        timeoutId = setTimeout(function() {

            // Si el valor maximo no es mayor al default o no es menor al minimo default o no es mayor min-inches a max-inches
            if (!(parseInt(max_inches_input.value) > parseInt(max_value_default) || parseInt(max_inches_input.value) < parseInt(min_value_default) || parseInt(min_inches_input.value) > parseInt(max_inches_input.value))) {
                console.log(min_inches_input.value, max_inches_input.value)
                localStorage.setItem('max-inches_', max_inches_input.value) // Pulgadas maximas
                load_products()
            } else {
                max_inches_input.value = max_value_default
                localStorage.setItem('max-inches_', max_value_default)
                load_products()
            }

            // Logica cuando se selecciona una etiqueta de pulgadas
            select_inches_tags(inches_values_list)

        }, 1000);

    });

}


// Funcion para seleccionar un rango de etiquetas de pulgadas
function select_inches_tags(inches_values_list) {

    let min_value = localStorage.getItem('min-inches_')
    let max_value = localStorage.getItem('max-inches_')

    // Unselect all

    for (let inches__ in inches_values_list) {

        // Al salir del elemento se deja el borde en su estao inicial
        let inches_tag_onrange = document.getElementById(`${inches_values_list[inches__]}-inches`);
        inches_tag_onrange.style.border = '2px solid #DEDEDE';
    }

    for (inches_value in inches_values_list) {

        let inch = parseInt(inches_values_list[inches_value])

        if (inch >= parseInt(min_value) && inch <= parseInt(max_value)) {
            // Se colorea el borde de la posible selección
            let inches_tag_onrange = document.getElementById(`${inches_values_list[inches_value]}-inches`);
            inches_tag_onrange.style.border = '2px solid #60af48';
        }

    }

}


// Establecer las etiquetas en el DOM
function set_inches_tags_filter(inches_values_list) {

    let inches_tag_container = document.querySelector('.inches-tag-filter_container');

    // Se limpia el contenedor de tags
    inches_tag_container.innerHTML = '';

    let inches_tag_container_content = '';
    for (inches_value in inches_values_list) {

        inches_tag_container_content += `<span id='${inches_values_list[inches_value]}-inches' class='onrange' inches-value='${inches_values_list[inches_value]}'>${inches_values_list[inches_value]}"</span>`;
    }

    inches_tag_container.innerHTML = inches_tag_container_content;

    // Logica cuando se selecciona una etiqueta de pulgadas
    on_select_inches_tag(inches_values_list)

    // Se cargan los eventlistener al cargar la pagina
    get_inches_filter_values(inches_values_list)
}

// Cuando se selecciona una etiqueta de pulgadas
function on_select_inches_tag(inches_values_list) {

    /* Teniendo en cuenta que cada elemento dentro de la lista de pulgadas
    existe dentro del DOM */

    // Inputs de pulgadas
    let min_inches_input = document.querySelector('.min-inches_input');
    let max_inches_input = document.querySelector('.max-inches_input');


    function on_click_tag(inches_tag_selected, inches) {

        console.log(min_tag_value_selected, max_tag_value_selected)


        // Si ya se selecciono las 2 posiciones posibles, se restablece y se selecciona solo 1
        if (min_tag_value_selected != 0 && max_tag_value_selected != 0) {

            for (let inches_ in inches_values_list) {

                let inches_tag_unselected = document.getElementById(`${inches_values_list[inches_]}-inches`);
                inches_tag_unselected.classList.remove("onrange");
                inches_tag_unselected.classList.remove("selected");

                var listenerFunction = () => mouseEnterHandler(inches_tag_unselected);

                inches_tag_unselected.addEventListener('mouseenter', function() {

                    let inches_value = inches_tag_unselected.getAttribute("inches-value")

                    for (let inches__ in inches_values_list) {

                        // Si es un valor menor al inicial1
                        if (inches_values_list[inches__] >= inches_value && inches_values_list[inches__] < inches_values_list[inches]) {

                            // Se colorea el borde de la posible selección
                            let inches_tag_onrange = document.getElementById(`${inches_values_list[inches__]}-inches`);
                            inches_tag_onrange.style.border = '2px solid #60af48';
                        }

                        // Si es un valor mayor al inicial
                        if (inches_values_list[inches__] <= inches_value && inches_values_list[inches__] > inches_values_list[inches]) {

                            // Se colorea el borde de la posible selección
                            let inches_tag_onrange = document.getElementById(`${inches_values_list[inches__]}-inches`);
                            inches_tag_onrange.style.border = '2px solid #60af48';
                        }

                    }

                });

                inches_tag_unselected.addEventListener('mouseleave', function() {

                    for (let inches__ in inches_values_list) {

                        // Al salir del elemento se deja el borde en su estao inicial
                        let inches_tag_onrange = document.getElementById(`${inches_values_list[inches__]}-inches`);
                        inches_tag_onrange.style.border = '2px solid #DEDEDE';
                        inches_tag_selected.style.border = '2px solid #60af48';

                    }

                });
            }

            inches_tag_selected.className += ' selected'

            // Valor de Min inches
            min_inches_input.value = inches_values_list[inches]
            localStorage.setItem('min-inches_', inches_values_list[inches])

            // Valor de Max inches
            max_inches_input.value = inches_values_list[inches]
            localStorage.setItem('max-inches_', inches_values_list[inches])

            inches_tag_selected.setAttribute('tag-status', 'selected')

            /* Se da valor al minimo y maximo */

            min_tag_value_selected = inches_values_list[inches]
            max_tag_value_selected = 0

            // Se cargan los productos
            load_products()

        } else {

            // Si solo hay un valor seleccionado

            if (min_tag_value_selected != 0 && max_tag_value_selected == 0) {

                let new_value = parseInt(inches_tag_selected.getAttribute('inches-value'))

                if (new_value < min_tag_value_selected) {

                    max_tag_value_selected = min_tag_value_selected;
                    min_tag_value_selected = new_value;

                    min_inches_input.value = min_tag_value_selected
                    max_inches_input.value = max_tag_value_selected

                    localStorage.setItem('min-inches_', min_tag_value_selected)
                    localStorage.setItem('max-inches_', max_tag_value_selected)


                } else {

                    max_tag_value_selected = new_value;
                    max_inches_input.value = max_tag_value_selected
                    localStorage.setItem('max-inches_', max_tag_value_selected)
                }

                for (let inches_ in inches_values_list) {
                    let inches_tag_unselected = document.getElementById(`${inches_values_list[inches_]}-inches`);

                    // Crear un clon del elemento sin los listeners
                    let clonedElement = inches_tag_unselected.cloneNode(true);
                    inches_tag_unselected.parentNode.replaceChild(clonedElement, inches_tag_unselected);

                    var onClickFunction = () => on_click_tag(clonedElement, inches_, min_tag_value_selected, max_tag_value_selected);

                    // Clonar el elemento elimina los listeners, ahora el nuevo clon no tiene ninguno
                    clonedElement.addEventListener('click', onClickFunction)
                }

                load_products() // Se cargan los productos

            }

        }
    }

    var min_tag_value_selected = parseInt(localStorage.getItem('min-inches-default_')) // Min value
    var max_tag_value_selected = parseInt(localStorage.getItem('max-inches-default_')) // Max value

    // Etiqueta
    for (let inches in inches_values_list) {

        let inches_tag_selected = document.getElementById(`${inches_values_list[inches]}-inches`);

        var onClickFunction = () => on_click_tag(inches_tag_selected, inches, min_tag_value_selected, max_tag_value_selected);

        // Se cargan los productos
        inches_tag_selected.addEventListener('click', function() {

            on_click_tag(inches_tag_selected, inches);

        });
    }

}





