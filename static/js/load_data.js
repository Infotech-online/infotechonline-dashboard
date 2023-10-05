
// Getting table data usign Ajax

function update_data() {

    let table = document.querySelector(".table-body")
    let counter = document.querySelector(".elements-loaded-text")
    let log_total_qty = document.querySelector(".log-total-qty")
    let last_log_date = document.querySelector(".last-log-date")
    let today_log_qty = document.querySelector(".today-log-qty")
    table.innerHTML = ""

    $.ajax({
        type: "POST",
        url: "/get-data",
        contentType: "application/json",
        dataType: 'json',
        success: function (result) {
            
            log_total_qty.innerHTML = result["log_qty"]
            last_log_date.innerHTML = result["last_log_date"]
            today_log_qty.innerHTML = result["today_log_qty"]
    
            let count = 0
            for(row in result["table_data"]) {
                
                let new_row = `
                <tr>
                    <td>${result["table_data"][row]["Fecha"]}</td>
                    <td>${result["table_data"][row]["Cliente"]}</td>
                    <td>${result["table_data"][row]["Valor"]}</td>
                    <td>${result["table_data"][row]["Guia"]}</td>
                    <td>${result["table_data"][row]["Estado"]}</td>
                </tr>`;
    
                table.innerHTML += new_row
                count++;
            };
            counter.innerHTML = `<e>${count}</e> elements are displayed`
        }
    });
}

update_data() // The data is loaded

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
