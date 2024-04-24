

// Tipo de catalogo

var corporate_shop = ajax_object.corporate_shop

console.log(corporate_shop)

// 1 == true
if (corporate_shop == "true") {
    corporate_shop = true;
} else {
    corporate_shop = false;
}

function update_brands() {

    let current_category = localStorage.getItem('category_');

    jQuery(document).ready(function($) {
        var data = {
            'action': 'get_brands_by_category',
            'category': current_category,
            'corporate_shop': corporate_shop
        }

        var ajaxurl = ajax_object.ajax_url;

        $.post(ajaxurl, data, function(response) {

            // Se limpia el espacio HTML de las marcas
            $('.brand-templante_items').html('');

            let brands = response;
            let brand_count = 0;

            for (brand in brands) {

                if (brand_count == 10) {
                    $('.brand-templante_items').append("<span class='show-more_button'>Mostrar mas</span>");
                    let brand_container = document.querySelector('.brand-templante_items');
        			brand_container.style.height = '370px';
                }

                brand_count += 1;

                // Si hay mas de 10 marcas agregar la clasr de "brand-hide"
                if(brand_count > 10){

                    // Si hay mas de 10 marcas se muestra el boton de mostrar mas marcas

                    // Se reemplaza la etiqueta (e) que por error aparece en el response
                    brand_element_hide_class = brands[brand].replace("class='brand-show'", "class='brand-hide'")
                    brand_element_style = brand_element_hide_class.replace("style='list-style-type: none'", "style='list-style-type: none; transform: translateX(-150px);'")
                    //style="list-style-type: none; transform: translateX(0px);"
                    brand_element = brand_element_style.replaceAll('<e>', '')

        			// Actualizar la página con las nuevas marcas
        			$('.brand-templante_items').append(brand_element);

                } else {

                    // Se reemplaza la etiqueta (e) que por error aparece en el response
                    brand_element = brands[brand].replaceAll('<e>', '')

        			// Actualizar la página con las nuevas marcas
        			$('.brand-templante_items').append(brand_element);

                    let brand_container = document.querySelector('.brand-templante_items');
        			brand_container.style.height = 'max-content';

                }
            }

			// Añadir marcas dando click
        	$('.brand-templante_items').each(function() {

        	    $(this).find('p').each(function() {
        	        $(this).remove();
        	    })

        		$(this).find('li').each(function() {

        			$(this).click(function() {

        			    let selected_brands = [];
                        let brands_  = localStorage.getItem('brands_')
                        selected_brands = brands_.split(',');

        				// Si la marca fue seleccionada
        				if (!selected_brands.includes($(this).find('input').attr('id'))) {

                            $(this).find('input').prop('checked', true ); // Cuando se selecciona
        					load_products('add_brand', $(this).find('input').attr('id'))

        				} else {

                            $(this).find('input').prop('checked', false ); // Cuando se deselecciona
        					load_products('delete_brand', $(this).find('input').attr('id'))

        				}
        			})
        		})
        	})

        	let list_elements = document.querySelectorAll('.brand-templante_items li')
	        brand_input_animations(list_elements)

	        let brand_hide = document.querySelectorAll('.brand-templante_items li.brand-hide')
	        console.log(brand_hide,'2')
	        product_brand_hidden(brand_hide)

            let selected_brands = []
	        let brands_  = localStorage.getItem('brands_') // Se obtienen las marcas de local storage

            // Si local storage no esta vacio
            if (brands_ != "" && brands_ != null && brands_ != undefined) {
                // Local storage devuelve una string separado por comas de las marcas
                selected_brands = brands_.split(','); // Se convierte en array el string (separado por comas)
            }

            // Cuando se refresca la pagina hacer check de las marcas guardadas en local storage
	        $('.brand-templante_items').each(function() {

                // Por cada marca
        		$(this).find('li').each(function(){
        			let itemId = $(this).find('input').attr('id');
        			// Si selected_brands tiene la ID de el elemento
        			if(selected_brands.includes(itemId)) {
        			    $(this).find('input').prop('checked', true ); // Se pone la propiedad en True
        			}
        		})
        	})

        })
    })
}

function change_current_category() {

    jQuery(document).ready(function($) {

        $('.category_list__button').click(function() {

            // Get url without params
            var current_url = window.location.href;
            var url_parts = current_url.split('?');
            var new_url = url_parts[0];

            var new_url_with_category = new_url + '?' + '&category=' + $(this).attr('id');

            // Update the URL status
            window.history.pushState({path: new_url_with_category}, '', new_url_with_category);

            localStorage.setItem('category_', $(this).attr('id'));

            $('.brand-templante_items').html('');

            $('.page-title').html($(this).attr('category-title'));

            // Limpiar las marcas
            localStorage.setItem('brands_', [])

            load_subcategory($(this).attr('id'))
            update_brands()
            if (localStorage.getItem('category_') == 'pantallas' || localStorage.getItem('category_') == 'televisores' || localStorage.getItem('category_') == 'monitores' || localStorage.getItem('category_') == 'monitores-industriales') {
                set_default_inches_filter_values('set_values')
            } else {
                load_products()
            }


        })

        $('.list__inside').click(function() {

            // Get url without params
            var current_url = window.location.href;
            var url_parts = current_url.split('?');
            var new_url = url_parts[0];

            var new_url_with_category = new_url + '?' + '&category=' + $(this).attr('id');

            // Update the URL status
            window.history.pushState({path: new_url_with_category}, '', new_url_with_category);

            localStorage.setItem('category_', $(this).attr('id'));

            $('.brand-templante_items').html('');

            $('.page-title').html($(this).attr('category-title'));

            // Limpiar las marcas
            localStorage.setItem('brands_', [])

            load_subcategory($(this).attr('id'))
            update_brands()
            if (localStorage.getItem('category_') == 'pantallas' || localStorage.getItem('category_') == 'televisores' || localStorage.getItem('category_') == 'monitores' || localStorage.getItem('category_') == 'monitores-industriales') {
                set_default_inches_filter_values('set_values')
            } else {
                load_products()
            }

        })
    });

}

function load_subcategory(current_category, type) {

    jQuery(document).ready(function($) {

        var data = {
            "action": "get_all_categories"
        }

        var ajaxurl = ajax_object.ajax_url;

        // Load subfilter for every category
        load_subfilters_fields();

        // If the category is not null or empty
        if (current_category != null && current_category != "" && current_category != "null") {

            $.post(ajaxurl, data, function(response) {

            }).done(function(response) {

                let categories = response;
                let current_category_title = "";
                let current_subcategory_title = "";

                for (category in categories) {

                    if (categories[category]['slug'] == current_category) {

                        current_category_title = category;

                        $('.page-title').html(current_category_title);
                    }
                }

                if (current_category_title == "") {

                    for (category in categories) {

                        for (subcategory in categories[category]['subcategories']) {

                            if (categories[category]['subcategories'][subcategory] == current_category) {

                                current_category_title = category;
                                current_subcategory_title = subcategory

                                $('.page-title').html(current_subcategory_title);

                            }
                        }
                    }
                }

                let subcategories = categories[current_category_title]['subcategories']
                let list_show_subitems = "";

                if(subcategories != null){
                	// array has elements
                	for (subcategory in subcategories) {

                	    list_show_subitems += `
        	            <div class='list__inside' id='${subcategories[subcategory]}' category-title='${subcategory}'>
                            <span>${subcategory}</span>
                        </div>
        		        `;
                	}
                }

                let list_type_class = ""

                let list_item = `
                <div class='current_category_list' style='margin-top: 40px; margin-bottom: 40px'>
                    <div class='category_list__item ${list_type_class}'>

                        <div class='category_list__button' id='${current_category}' category-title='${current_category_title}'>
                            <div class='category_title'>
                                <span class='nav__link'>${current_category_title}</span>
                            </div>

                        </div>

                        <div class='current_list__show'>
                            ${list_show_subitems}
                        </div>
                    </div>
                </div>
                `;

                $('.current_category_nav').html('');
                $('.current_category_nav').append(list_item);

                change_current_category();
            })

        } else { // If the category is empty print "Sin categoria seleccionada"
            $('.current_category_nav').html('');
            $('.current_category_nav').append('<p>Sin categoría seleccionada.</p>');
        }

    })
}


function load_categories() {

	jQuery(document).ready(function($) {

		var data = {
			'action': 'get_all_categories',
		};

		var ajaxurl = ajax_object.ajax_url;

		let business_categories = ["Memorias RAM", "UPS", "Redes", "Almacenamiento", "Proyectores", "Impresoras de Oficina", "Monitores industriales"] // Business categories

		$.post(ajaxurl, data, function(response) {

		    console.log(response)

		    let categories = response;

            let all_category_items = '';
		    for (category in categories) {

		        // Si es el catalogo corporativo
		        if (corporate_shop == true) {

                    if (business_categories.includes(category)) {

                        let subcategories = categories[category]['subcategories'];
                        let list_show_subitems = "";
                        let arrow_defined = "";
                        let list_type_class = "";

                        if(subcategories != null){

                            arrow_defined = "<img src='https://jgallego.pythonanywhere.com/cdn/woocommerce-infotechonline/woocommerce-resources/bx-chevron-right.svg' class='list_arrow'>";
                            list_type_class = "category_list__click";

                        	// array has elements

                        	for (subcategory in subcategories) {

                        	    list_show_subitems += `
                	            <div class='list__inside' id='${subcategories[subcategory]}' category-title='${subcategory}'>
                                    <span>${subcategory}</span>
                                </div>
                		        `;
                        	}
                        }


        		        let list_item = `
            		    <div class='category_list__item ${list_type_class}'>
                            <div class='category_list__button' id='${categories[category]['slug']}' category-title='${category}'>
                                <div class='category_title'>
                                    <!--<img src="${categories[category]['image']}" class='category_list__image'>-->
                                    <span class='nav__link'>${category}</span>
                                </div>
                                ${arrow_defined}
                            </div>

                            <div class='list__show'>
                                ${list_show_subitems}
                            </div>

                        </div>`;

                        all_category_items += list_item

                    }

		        } else {

		            if (!business_categories.includes(category) && category != "Corporativo") {

                        let subcategories = categories[category]['subcategories'];
                        let list_show_subitems = "";
                        let arrow_defined = "";
                        let list_type_class = "";

                        if(subcategories != null){

                            arrow_defined = "<img src='https://jgallego.pythonanywhere.com/cdn/woocommerce-infotechonline/woocommerce-resources/bx-chevron-right.svg' class='list_arrow'>";
                            list_type_class = "category_list__click";

                        	// array has elements

                        	for (subcategory in subcategories) {

                        	    list_show_subitems += `
                	            <div class='list__inside' id='${subcategories[subcategory]}' category-title='${subcategory}'>
                                    <span>${subcategory}</span>
                                </div>
                		        `;
                        	}
                        }


        		        let list_item = `
            		    <div class='category_list__item ${list_type_class}'>
                            <div class='category_list__button' id='${categories[category]['slug']}' category-title='${category}'>
                                <div class='category_title'>
                                    <!--<img src="${categories[category]['image']}" class='category_list__image'>-->
                                    <span class='nav__link'>${category}</span>
                                </div>
                                ${arrow_defined}
                            </div>

                            <div class='list__show'>
                                ${list_show_subitems}
                            </div>

                        </div>`;

                        all_category_items += list_item

    		        }

		        }

		    }

            $('.category_list').append(all_category_items);

            let list_elements = document.querySelectorAll('.category_list__click')

            list_elements.forEach(list_element => {

                list_element.addEventListener('mouseenter', () => {

                    list_element.classList.toggle('arrow')

                    let height = 0;
                    let menu = list_element.querySelector('.list__show');

                    if(menu.clientHeight == "0") {
                        height = menu.scrollHeight;
                    }

                    menu.style.height = `${height}px`;
                })

                list_element.addEventListener('mouseleave', () => {

                    list_element.classList.toggle('arrow')

                    let height = 0;
                    let menu = list_element.querySelector('.list__show');

                    menu.style.height = `${height}px`;
                })
            })

            change_current_category();


		});
	});
}


function load_subfilters_fields() {

    jQuery(document).ready(function($) {

        if (localStorage.getItem('category_') == 'pantallas' || localStorage.getItem('category_') == 'televisores' || localStorage.getItem('category_') == 'monitores' || localStorage.getItem('category_') == 'monitores-industriales') {

            $('.inches-filter_container').css('display', 'flex');
            $('.inches_title').css('display', 'flex');

        } else {
            $('.inches-filter_container').css('display', 'none');
            $('.inches_title').css('display', 'none');
        }
    })
}

// For the first load

load_subfilters_fields();
load_subcategory(localStorage.getItem('category_'));
update_brands()
load_categories()