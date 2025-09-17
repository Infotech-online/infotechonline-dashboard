
function delete_dom_elements() {

    jQuery(document).ready(function($) {

        let element_p = $("#customer_details").next("p");
        element_p.css("display", "none");
    })

}

delete_dom_elements()

document.addEventListener('DOMContentLoaded', function() {
  var formularioBusqueda = document.querySelector('.dgwt-wcas-search-form');

  formularioBusqueda.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
      event.preventDefault(); // Evita el comportamiento por defecto del formulario al presionar "Enter"
    }
  });
});