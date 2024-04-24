// This script needs Anime.js Libraries


// Add brand chekout input animation when the mouse enter on the container
function brand_input_animations(list_elements) {

    let list_elements_li = list_elements

    list_elements_li.forEach(list_element => {

        let span_element = list_element.querySelector('span');

        list_element.addEventListener('mouseenter', () => {

            anime({
              targets: span_element,
              translateX: 5
            });

        })

        list_element.addEventListener('mouseleave', () => {

            anime({
              targets: span_element,
              translateX: 0
            });

        })
    })
}



// Brand product animation when the mouse enter on the product container (Li)

function product_brand_tag_animation(products) {

    let list_elements_li = products

    list_elements_li.forEach(list_element => {

        let brand_tag = list_element.querySelector('.brand-tag');

        list_element.addEventListener('mouseenter', () => {

            anime({
              targets: brand_tag, // reemplaza 'elemento' con tu selector de elemento
              translateY: '50px',
            });

        })

        list_element.addEventListener('mouseleave', () => {

            anime({
              targets: brand_tag, // reemplaza 'elemento' con tu selector de elemento
              translateY: '-30px',
            });

        })
    })
}


function product_brand_hidden(brands) {

    console.log(brands)

    let show_more_button = document.querySelector('.show-more_button');

    show_more_button.addEventListener('click', () => {

        let brand_container = document.querySelector('.brand-templante_items');
        brand_container.style.height = 'max-content';
        show_more_button.style.display = 'none';

        anime({
          targets: brands,
          translateX: '0px',
          delay: anime.stagger(100) // increase delay by 100ms for each elements.
        });

    })

}




