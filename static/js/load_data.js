
// Number to currency format

const currency = function(number){
    return new Intl.NumberFormat('es', {style: 'currency', currency: 'COP', minimumFractionDigits: 0}).format(number);
};

// Getting table data usign Ajax

// Pagination
let page_text = document.querySelector(".page-text")

function update_data(page) {

    let table = document.querySelector(".table-body")
    let counter = document.querySelector(".elements-loaded-text")
    let log_total_qty = document.querySelector(".log-total-qty")
    let last_log_date = document.querySelector(".last-log-date")
    let today_log_qty = document.querySelector(".today-log-qty")

    table.innerHTML = ""

    $.ajax({
        type: "POST",
        url: "/infotech-data",
        data: {"page": page},
        //contentType: "application/json;charset=UTF-8",
        //dataType: 'json',
        success: function (result) {
            
            log_total_qty.innerHTML = result["log_qty"]
            last_log_date.innerHTML = result["last_log_date"]
            today_log_qty.innerHTML = result["today_log_qty"]
            page_text.innerHTML = "Page " + page

            let count = 0
            for(row in result["products"]) {
                
                let new_row = `
                <tr>
                    <th scope="row">${result["products"][row]["id"]}</th>
                    <td>${result["products"][row]["sku"]}</td>
                    <td>${currency(result["products"][row]["regular_price"])}</td>
                    <td>${result["products"][row]["name"]}</td>
                </tr>`;
    
                table.innerHTML += new_row
                count++;
            };
            counter.innerHTML = `<e>${count}</e> elements are displayed`

            if(count >= 100) {
                $( ".forward-icon" ).removeClass('disabled');
            } else {
                $( ".forward-icon" ).addClass('disabled');
            }
        }
    });
}

let current_page = 1
update_data(current_page) // The data is loaded (first load)

// Pagination

$('.forward-icon').click(function () {

    if($(this).hasClass("disabled")) {
        console.log("current page - ", current_page)
    } else {
        $(".back-icon").removeClass('disabled');
        current_page = current_page + 1
        update_data(current_page)
    }
})

$('.back-icon').click(function () {
    
    if($(this).hasClass("disabled")) {
        console.log("current page - ", current_page)
    } else {
        current_page = current_page - 1
        update_data(current_page)
        if(current_page == 1) {
            $(".back-icon").addClass('disabled'); 
        }
    }
})

// Update section

$('.update-button').click(function () {

    let update_option = {"option": "0"}
    if($('.only-empty-cells').is(':checked')) { update_option = {"option": "0"};}
    if($('.all-cells').is(':checked')) { update_option = {"option": "1"};}

    $.ajax({
        type: "POST",
        url: "/update",
        data: update_option,
        dataType: 'json',
        beforeSend: function () {
            $('.load-message').removeClass('display-none')
            $('.last-update-message').addClass('display-none')
            $('.success-message').addClass('display-none')
        },
        success: function (data) {
        },
        complete: function () {
            $('.load-message').addClass('display-none')
            $('.success-message').removeClass('display-none')
            update_data()
        },
    });
});
