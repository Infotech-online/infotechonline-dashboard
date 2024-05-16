// Juan Carlos Gallego Barona

// Tipo de catalogo

var corporate_shop = ajax_object.corporate_shop

// Si es el catalogo corporativo
if (corporate_shop == "true") {
    corporate_shop = true;
} else {
    corporate_shop = false;
}


// Verificar si la página se está recargando
window.addEventListener('beforeunload', function(event) {
    // Almacenar un valor en localStorage antes de que la página se recargue
    localStorage.setItem('reloaded', true);
});

// Verificar si la página se ha recargado
window.addEventListener('load', function(event) {

    // Verificar si la variable 'reloaded' está presente en localStorage
    if (localStorage.getItem('reloaded')) {

        // La página se ha recargado
        console.log('La página se ha recargado');

    } else {

        // La página se ha cargado por primera vez (no recargada)
        console.log('La página se ha cargado por primera vez');
    }
});

function get_url_params() {

    var current_url = window.location.href; // Se obtienen la URL actual en una string
    var url_params = current_url.split('?')[1]; // Se obtiene la parte de los parametros de la URL

    // Decodificar la cadena de consulta
    var decoded_filters_params = decodeURIComponent(url_params);

    // Se establecen las variables como vacias
    var current_params = []
    var current_category = null;
    var first_load = false

    // Se maneja la string de la URL actual se separa por &
    decoded_filters_params.split('&').forEach(function(item) {
        // Se separa en dos partes, la parte [0] es el titulo y la parte [1] el valor
        var parts = item.split('=');

        // Si es categoria
        if (parts[0] == "category") {
            current_category = parts[1] // Se cambia el valor de la categoria
        } else if (parts[0] == 'first_load') {
            // Si es el parametro de inicio
            first_load = true
        } else {
            // Si es marca
            var value = parts[1];
            current_params.push(value) // Se almacena el valor dentro de las marcas
        }
    });

    // Si la categoria actual es diferente de la categoria almacenada dentro de local storage
    if (current_category != localStorage.getItem('category_') && first_load == false) {

        // Se establece la categoria actual dentro de local storage
        localStorage.setItem('category_', current_category);
        // Se limpian las marcas
        localStorage.setItem('brands_', []);
    } else {
        // Se establece la categoria actual dentro de local storage
        localStorage.setItem('category_', current_category);
        localStorage.setItem('brands_', current_params);
    }

    // Se retorna una lista con las marcas y categoria actual
    return [current_params, current_category]
}

function update_url_status(selected_brands=null) {

    jQuery(document).ready(function($) {

        if (typeof selected_brands === 'string') {
            selected_brands = selected_brands.split(',');
            console.log(selected_brands, "split")
        }

        // Update URL Status
        var brand_filter_array = $.param({ "brand_filter": selected_brands });
        var current_url = window.location.href;

        if (!localStorage.getItem('reloaded')) {

            // Update URL Status
            var brand_filter_array = $.param({ "brand_filter": selected_brands });
            var current_url = window.location.href;

            if (!current_url.includes("brand_filter")) {

                var url_parts = current_url.split('?');
                var new_url = url_parts[0];
                var new_url = new_url + '?' + brand_filter_array + '&category=' + localStorage.getItem('category_');

            	window.history.pushState({path: new_url}, '', new_url);

            } else {

                var url_params = current_url.split('?')[1];

                // Decodificar la cadena de consulta
                var decoded_filters_params = decodeURIComponent(url_params);

                // Convertir la cadena de consulta decodificada en un objeto de parámetros
                var current_params = [];
                var current_category = null

                decoded_filters_params.split('&').forEach(function(item) {
                    var parts = item.split('=');
                    var value = parts[1];

                    if (parts[0] != 'category') {
                        current_params.push(value)
                    }

                });

                for (brand in selected_brands) {
                    if (!current_params.includes(selected_brands[brand])) {
                        current_params.push(selected_brands[brand])
                    }
                }

                for (brand in current_params) {
                    console.log(selected_brands, 'delete')
                    if (!selected_brands.includes(current_params[brand])) { // Cuando se refresca la pagina se borran todos los elementos de selected brands por ende se borraran todas las marcas
                        for (let i = current_params.length - 1; i >= 0; i--) {
                            console.log(current_params[brand], 'delete')
                            if (current_params[i] === current_params[brand]) {
                                current_params.splice(i, 1);
                            }
                        }
                    }
                }
                console.log(current_params)
                localStorage.setItem('brands_', current_params);

                var brand_filter_array = $.param({ "brand_filter": current_params });

                var url_parts = current_url.split('?');
                var new_url = url_parts[0];
                var new_url = new_url + '?' + brand_filter_array + '&category=' + localStorage.getItem('category_');

            	window.history.pushState({path: new_url}, '', new_url);
            }

        } else {

            var brand_filter_array = $.param({ "brand_filter": selected_brands });

            var url_parts = current_url.split('?');
            var new_url = url_parts[0];
            var new_url = new_url + '?' + brand_filter_array + '&category=' + localStorage.getItem('category_');

        	window.history.pushState({path: new_url}, '', new_url);

            load_products('reloaded')
            localStorage.removeItem('reloaded');
        }

    });
}

function load_products(action, input_id) {

    let selected_brands = [];
    let brands_  = localStorage.getItem('brands_') // Se obtienen las marcas de local storage

    // Si local storage no esta vacio
    if (brands_ != "" && brands_ != null && brands_ != undefined) {
        // Local storage devuelve una string separado por comas de las marcas
        selected_brands = brands_.split(','); // Se convierte en array el string (separado por comas)
    }

    // Se declara jQuery
	jQuery(document).ready(function($) {

	    let url_params = get_url_params();
	    // let current_category = url_params[1]
	    let current_category = localStorage.getItem('category_');

        // Se se selecciono una nueva marca (agregar marca a los filtros)
        if (action == 'add_brand') {

            // Se agrega la nueva marca a selected_brands
            selected_brands.push(input_id);
            // Se guarda en el local storage (brands_)
            localStorage.setItem('brands_', selected_brands)
        }

        // Se se deselecciono una nueva marca (eliminar marca de los filtros)
        if (action == 'delete_brand') {

            // Se busca el elemento en la lista para ser eliminado
            for (let i = selected_brands.length - 1; i >= 0; i--) {

                // Se elimina el elemento cuando sea igual al seleccionado
                if (selected_brands[i] === input_id) {
                    selected_brands.splice(i, 1);
                }
            }

            // Se actualiza el local storage con los nuevos elementos deseleccionados
            localStorage.setItem('brands_', selected_brands)
        }

        for (let i = selected_brands.length - 1; i >= 0; i--) {

            if (selected_brands[i] === "") {
                selected_brands.splice(i, 1);
            }
        }

		var selected_brands_parsed = JSON.stringify(selected_brands);
		var ajaxurl = ajax_object.ajax_url;

		// Test
		let inches_filter = null
		if (localStorage.getItem('category_') == 'pantallas' || localStorage.getItem('category_') == 'televisores' || localStorage.getItem('category_') == 'monitores' || localStorage.getItem('category_') == 'monitores-industriales' || localStorage.getItem('category_') == 'monitores-de-escritorio' || localStorage.getItem('category_') == 'pantallas-corporativo') {

            inches_filter = [parseInt(localStorage.getItem('min-inches_')), parseInt(localStorage.getItem('max-inches_'))]; // 0 pos = min, 1 pos = max

		}

		inches_filter_parsed =  JSON.stringify(inches_filter);

		var data = {
			'action': 'ajax_next_posts',
			'posts_per_page': 100,  // Número de productos por página
			'post_offset': 0, // Desplazamiento de la consulta
			'current_category': localStorage.getItem('category_'),
			'brand_list': selected_brands_parsed,
			'inches_filter': inches_filter_parsed,
			'corporate_shop': corporate_shop
		};

		update_url_status(selected_brands)

		$.post(ajaxurl, data, function(response) {

		}).done(function(response) {

            $('.products').html('');
			$('.woocommerce-result-count').html('');

			// Manejar la respuesta aquí
			var result = JSON.parse(response);
			console.log(result)
			var new_posts_html = result[0];

			// Actualizar la página con los nuevos productos
			$('.products').append(new_posts_html);
			$('.woocommerce-result-count').html(`Mostrando ${result[1]} resultados`);


			let products = document.querySelectorAll('.products li')
			product_brand_tag_animation(products)

		})
	});
}

// First load

// Se obtienen los parametros de la URL al recargar la pagina o iniciarla
get_url_params()

if (!localStorage.getItem('reloaded')) {
    load_products()
} else {
    // localStorage.setItem('brands_', '') // Temporal
    let brands = localStorage.getItem('brands_')
    update_url_status(brands)
}

// Se limpia el apartado de marcas de posibles errores de impresion (espacios en blanco)
jQuery(document).ready(function($) {

	// Se obtienen las marcas seleccionadas
	$('.brand-templante_items').each(function() {

	    $(this).find('p').each(function() {
	        $(this).remove();
	    })
	})
});