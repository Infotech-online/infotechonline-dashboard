
/*
anime({
    targets: '.table-content',
    background: 'linear-gradient(90deg, rgba(255,255,255,1) 0%, rgba(235,235,235,1) 50%, rgba(232,232,232,1) 100%)',
    easing: 'easeInOutQuad',
    loop: true,
    duration: 3000
});*/

// Loading Animation (with gradiants)

function loading_animation() {

    // Create a timeline with default parameters
    anime({
        targets: '.table-content',
        keyframes: [
            { background: 'linear-gradient(90deg, rgba(229,229,229,1) 0%, rgba(255,255,255,1) 100%)' }
        ],
        easing: 'linear',
        direction: 'alternate',
        loop: true
    });
}

// loading_animation()

let selectedItems = [];

$('.brand-templante_items').each(function() {
    $(this).find('li').each(function(){
        if ($(this).is(':checked')) {
            selectedItems.push($(this).attr('id'));
        }
    })
})

console.log(selectedItems);