from flask import Flask, request, render_template, session, url_for, redirect, send_file
import requests
from dotenv import dotenv_values
import time
from datetime import datetime
import json

app = Flask(__name__, template_folder='templates', static_folder='static')

# Env Vars
env = dotenv_values(".env")

# Local Libs
from local_libs.ingram import ingramConnection
from local_libs.intcomex import intcomexConnection
from local_libs.woocommerce import wooConnection

ingram = ingramConnection()
intcomex = intcomexConnection()
woo = wooConnection()

@app.route('/')
def dashboard():

    # Display the dashboard
    return render_template("dashboard.html")

@app.route('/local-data', methods=["POST"])
def infotech_data():

    if request.method == "POST":

        # Get request args
        page = request.form["page"]

        # Return a json with data
        products = woo.mconsult().get("products", params={'per_page': 100, 'order': 'asc', 'page': page}).json() # WooCommerce Productproducts

        # Get image data
        with open('products_imgs.json') as f:
            imgs = json.load(f)

        # Get log data
        with open('logs.json') as f:
            logs_data = json.load(f)

        logs_qty = 0
        today_log_qty = 0
        for pos, log in enumerate(logs_data["logs"]):
            logs_qty+=1
            if log["date"].find(f"{datetime.now().strftime('%Y-%m-%d')}") != -1:
                today_log_qty+=1
            
        # Dollar Price
        """request_currencies = requests.get("http://apilayer.net/api/live?access_key=35fecb58061d2dcd76ce985b306bcc07&currencies=COP&source=USD&format=1")
        response = request_currencies.json()
        dollar = response["quotes"]["USDCOP"]"""

        # Save data
        data = {}
        data["products"] = products
        data["logs"] = logs_data["logs"]
        data["logs_qty"] = logs_qty

        if len(logs_data["logs"]) > 0:
            data["last_log_date"] = logs_data["logs"][logs_qty-1]["date"]
        else:
            data["last_log_date"] = "(Null)"

        data["today_log_qty"] = today_log_qty
        # data["dollar"] = dollar
        data["imgs"] = imgs

        return data
    
    else:
        return "No deberias estar viendo esta pagina."

@app.route('/ingram-update', methods=["POST"])
def ingram_update():

    if request.method == "POST":

        # Products SKU
        # Productos a los cuales se les va a cambiar el precio

        init_time = time.time()
        print(init_time)

        with open('ingram_products.json') as f:
            products_data = json.load(f)

        # Log data
        qty = 0
        products = []

        # Prices
        prices = ingram.return_prices()

        # Stock
        stock = ingram.return_all_stock()

        for category in products_data:  # Categories
            for sku in products_data[category]:  # Sku and Prices

                # Ingram part number
                ingram_pnumber = products_data[category][sku]["ingramSku"]
                
                # Calc the final price
                cop_price = int(prices[sku])
                profit = (cop_price * 0.13) + cop_price
                final_price_with_IVA = profit * 1.19

                # Stock
                if stock[ingram_pnumber] > 0:
                    stock_status = "instock"
                else:
                    stock_status = "outofstock"

                print(sku, stock_status)

                if (int(final_price_with_IVA) != int(products_data[category][sku]["price"])) or (products_data[category][sku]["stock"] != stock_status):
                    
                    # WooCommerce Product
                    product = woo.mconsult().get("products", params={'sku': sku, 'per_page': 1}).json()

                    data = {"regular_price": f"{int(final_price_with_IVA)}", "stock_status": f"{stock_status}"}
                    woo.mconsult().put(f"products/{product[0]['id']}", data).json()  # Product Update

                    # Log
                    data_log = {
                        "id": product[0]["id"],
                        "sku": f"{sku}",
                        "ingrampartnumber": ingram_pnumber,
                        "stock": stock_status,
                        "past_price": f"{product[0]['price']}",
                        "regular_price": f"{int(final_price_with_IVA)}"
                    }

                    qty += 1
                    products.append(data_log)

                    products_data[category][sku]["price"] = int(final_price_with_IVA)
                    products_data[category][sku]["stock"] = stock_status
                    upd_product = json.dumps(products_data, indent=4)

                    with open('ingram_products.json', 'w') as file:
                        file.write(upd_product)

        # Save the Log in "logs.json"
        with open('logs.json') as f:

            logs_data = json.load(f)
            logs_data_list = logs_data["logs"]

            new_log = {
                "date": f"{datetime.now().strftime('%Y-%m-%d')} / {datetime.now().time().strftime('%H:%M:%S')}",
                "qty": qty,
                "products": products
            }

            logs_data_list.append(new_log)
            logs_data["logs"] = logs_data_list
            log = json.dumps(logs_data, indent=4)

        with open('logs.json', 'w') as file:
            file.write(log)

        end_time = time.time()
        total_time = end_time - init_time
        print(total_time)

        return "Success", 201  # Return success
    else:
        return "No deberias estar viendo esta pagina. <a href='/'>VOLVER ATRAS</a>"

@app.route('/intcomex-update')
def intcomex_update():

    # Get product data of local DB
    with open('intcomex_products.json') as f:
        products_data = json.load(f)

    for category in products_data:  # Categories
        for id in products_data[category]:  # Sku

            provider_sku = products_data[category][id][1]

            product = intcomexConnection().get_single_product(provider_sku)
            product_price = str(product["Price"]["UnitPrice"])

            update_data = {
                "regular_price": product_price,
                "stock_quantity": product["InStock"]
            }

            woo.mconsult().put(f"products/{id}", update_data).json()

    return "Success", 201

"""
@app.route('/intcomex-add')
def intcomex_add():

    # Get categories
    with open('categories.json') as f:
        categories = json.load(f)

    # New products
    new_products = {
        "101045": "AB355NXT01",
        "101046": "AB360NXT02"
    }

    for product in new_products:

        product = intcomex.get_single_product(new_products[product])

        if product.ok:

            data = {
                "name": product["Description"],
                "type": "simple",
                "regular_price": product["Price"]["UnitPrice"],
                "description": "",
                "short_description": "",
                "categories": [
                    {
                        "id": 9
                    },
                    {
                        "id": 14
                    }
                ],
            }

            print(wc.post("products", data).json())

    return "Success", 201 """

"""
Data visualization ----------------------------------------------------------------------------------------------------
This code is used to retrieve information
"""

@app.route('/logs')
def logs():

    with open('logs.json') as f:
        logs_data = json.load(f)

    return logs_data

@app.route('/producto/<id>')
def inspeccionar_producto(id):

    return woo.mconsult().get(f"products/{id}").json()  # WooCommerce Product

@app.route('/get-categories')
def get_categories():

    categories = woo.mconsult().get(f"products/categories", params={'per_page': 100}).json()

    cats_short = {}
    for category in categories:
        cats_short[str(category['id'])] = str(category["name"])
        
    return cats_short   # WooCommerce Product

@app.route("/intcomex-products")
def intcomex_products():

    return intcomex.get_products()

@app.route("/ingram-products")
def ingram_products():

    return ingram.get_products()[0]

@app.route("/woo-products")
def wordpress_products():

    return woo.get_all_prods()

@app.route("/woo-imgs")
def wordpress_imgs():

    return woo.get_all_imgs()

if __name__ == '__main__':

    app.run(debug=True, host="0.0.0.0", port=1010)

# π - 2023
# An Infotech Solution