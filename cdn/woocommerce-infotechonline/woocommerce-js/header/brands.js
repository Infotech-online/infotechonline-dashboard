
function add_brand_submenu() {

    jQuery(document).ready(function($) {

        var ajaxurl = ajax_object.ajax_url;

		var data = {
			'action': 'get_submenu_brands',
		};

		let all_brands_container = '';

		$.post(ajaxurl, data, function(response) {

		}).done(function(response) {

            // La petición se realizó con exito

            let brand_letters = response[0]
            console.log(brand_letters)
            let brands = response[1];
            console.log(brands)

            let brand_url = '/catalogo/?brand_filter%5B%5D=&category=null&first_load';
            for (letter in brand_letters) {

                if (brand_letters[letter] != "") {


                    // Esta variable almacenara todos los <a> de marcas
                    let all_brands = '';
                    let brand_count = 0;
                    let large_container_class = ''

                    // Si la marca inicia con la misma letra
                    for (brand in brands) {

                        if (brands[brand][0] == brand_letters[letter]) {

                            brand_count += 1;

                            // Si hay mas cuatro o mas marcas
                            if (brand_count >= 3) {
                                large_container_class = 'large-brand_container';
                            }
                            brand_url = `/catalogo-live/?brand_filter%5B%5D=${brands[brand]}&category=null&first_load`;
                            all_brands = all_brands + `<a href='${brand_url}'>${brands[brand]}</a>`;
                        }
                    }

                    all_brands_container = all_brands_container + `
                    <div class="submenu-letter_container">
                        <span class='submenu-brand-letter_title'>${brand_letters[letter]}.</span>
                        <div class="brand_container ${large_container_class}">
                            ${all_brands}
                        </div>
                    </div>`;
                }


            }

            // Se añaden todas las marcasyo s y el submenu

            let submenu_content = `
            <div class="submenu-content_container">
                <div class="submenu-content">
                    ${all_brands_container}
                </div>
            </div>
            <script src='https://jgallego.pythonanywhere.com/cdn/woocommerce-infotechonline/woocommerce-js/animations/header_submenu.js'></script>`;

            $('.brand-nav_container').append(submenu_content);

        }).fail(function(jqXHR, textStatus, errorThrown) {
            // Esta función se ejecuta si la solicitud falla
            console.error('Error en la solicitud: ' + textStatus, errorThrown);

        }).always(function() {
            // Esta función se ejecuta siempre, ya sea éxito o fallo de la solicitud
            console.log('Solicitud completada');
        });

    })

}

add_brand_submenu();
