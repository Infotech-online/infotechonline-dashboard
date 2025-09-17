
// Drowpdown animaciones
function dropdown_menu() {

    // Cuando el mouse este encima de la categoria se desplegara el submenu

    let brand_submenu_container = document.querySelector('.brand-nav_container');
    let submenu = document.querySelector('.submenu-content_container');

    brand_submenu_container.addEventListener('mouseenter', () => {

        submenu.style.display = 'flex'

        anime({
          targets: submenu,
          opacity: '1'
        });

    })

    brand_submenu_container.addEventListener('mouseleave', () => {

        submenu.style.display = 'none'

        anime({
          targets: submenu,
          opacity: '0'
        });

    })

}

dropdown_menu();

function add_brand_submenu_animations() {

    let list_elements = document.querySelectorAll('.submenu-content_container a');

    list_elements.forEach(list_element => {

        list_element.addEventListener('mouseenter', () => {

            list_element.style.transform = 'translateY(-5px)'

        })

        list_element.addEventListener('mouseleave', () => {

            list_element.style.transform = 'translateY(0px)';

        })
    })

}

add_brand_submenu_animations()
