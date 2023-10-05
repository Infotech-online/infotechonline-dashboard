from flask import Flask, request, render_template, session, url_for, redirect, send_file
import requests
from dotenv import dotenv_values
from woocommerce import API
import PyCurrency_Converter
import bs4
import random
import os
import time
import datetime
import json
import smtplib
import time
import hashlib

app = Flask(__name__, template_folder='templates', static_folder='static')

# Env Vars
env = dotenv_values(".env")

# Session vars
app.secret_key = "super secret key"

# WooCommerce API Credentials
wc = API(
    url=env["URL"],
    consumer_key=env['CONSUMER_KEY'],
    consumer_secret=env['CONSUMER_SECRET'],
    version="wc/v3"
)

@app.route('/')
def dashboard():

    # Display the dashboard
    return render_template("dashboard.html")

@app.route('/infotech-data', methods=["POST"])
def infotech_data():

    if request.method == "POST":

        # Get request args
        page = request.form["page"]

        # Return a json with data
        products = wc.get("products", params={'per_page': 100, 'order': 'asc', 'page': page}).json() # WooCommerce Productproducts

        #Get log data
        with open('logs.json') as f:
            logs_data = json.load(f)

        # Dollar Price
        request_currencies = requests.get("http://apilayer.net/api/live?access_key=35fecb58061d2dcd76ce985b306bcc07&currencies=COP&source=USD&format=1")
        response = request_currencies.json()
        dollar = response["quotes"]["USDCOP"]

        # Save data
        data = {}
        data["products"] = products
        data["logs"] = logs_data
        data["dollar"] = dollar

        return data
    
    else:

        return "No deberias estar viendo esta pagina."

@app.route('/price-update')
def submit():

    # Products SKU
    # Productos a los cuales se les va a cambiar el precio

    init_time = time.time()
    print(init_time)

    with open('ingram_products.json') as f:
        products_data = json.load(f)

    # Log data
    qty = 0
    products = []

    # Dollar Price
    request_currencies = requests.get(
        "http://apilayer.net/api/live?access_key=35fecb58061d2dcd76ce985b306bcc07&currencies=COP&source=USD&format=1")
    response = request_currencies.json()

    for category in products_data:  # Categories
        for sku in products_data[category]:  # Sku and Prices

            product_dollar_price = products_data[category][sku][1]
            # This var is set in env file
            usd_to_cop = response["quotes"]["USDCOP"]

            # Calc the final price
            cop_price = float(product_dollar_price) * float(usd_to_cop)
            profit = (cop_price * 0.13) + cop_price
            final_price_with_IVA = profit * 1.19

            # WooCommerce Product
            product = wc.get("products", params={
                             'sku': sku, 'per_page': 100}).json()

            data = {"regular_price": f"{int(final_price_with_IVA)}"}
            wc.put(f"products/{product[0]['id']}",
                   data).json()  # Product Update

            # Log
            data_log = {
                "id": product[0]["id"],
                "sku": f"{sku}",
                "usd_cop_price": usd_to_cop,
                "past_price": f"{product[0]['price']}",
                "regular_price": f"{int(final_price_with_IVA)}"
            }

            qty += 1
            products.append(data_log)

    # Save the Log in "logs.json"
    with open('logs.json') as f:

        logs_data = json.load(f)
        logs_data_list = logs_data["logs"]

        from datetime import datetime

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

    return str(total_time)  # Return success

@app.route('/logs')
def logs():

    with open('logs.json') as f:
        logs_data = json.load(f)

    return logs_data

@app.route('/especific-description-update')
def description_update():

    # It is used to update the Warranty in the description of the products

    # WooCommerce Product
    products = wc.get("products", params={'per_page': 100}).json()

    for product in products:

        # Updating the description
        description = product["description"]

        if description.find("Garant") == -1:

            position = "</ul>"
            new_element = "<li>Garantía: 1 año</li>\n"

            # The description is parsed (convert to list)
            parsed_description = description.split()

            # Get Word Index (-1 is needed to add the word in the left position)
            word_index = parsed_description.index(position) - 1
            parsed_description[word_index] += new_element

            # Convert the parsed description to String
            new_description = ' '.join([str(element)
                                       for element in parsed_description])

            update_data = {
                "attributes": [{
                    "id": 19,
                    "name": "Garantía",
                    "options": [
                        "1 año"
                    ],
                    "position": 2,
                    "variation": False,
                    "visible": True
                }],
                "description": new_description
            }

            for att in product["attributes"]:
                update_data["attributes"].append(att)

            wc.put(f"products/{product['id']}",
                   update_data).json()  # Product Update

    return "success"

@app.route('/producto/<id>')
def inspeccionar_producto(id):

    return wc.get(f"products/{id}").json()  # WooCommerce Product

@app.route('/get-categories')
def get_categories():

    categories = wc.get(f"products/categories", params={'per_page': 100}).json()

    cats_short = {}
    for category in categories:
        cats_short[str(category['id'])] = str(category["name"])
        
    return cats_short   # WooCommerce Product

@app.route('/intcomex-update')
def intcomex_update():

    # Get product data of local DB
    with open('intcomex_products.json') as f:
        products_data = json.load(f)

    url = env["INTCOMEX_URL"]
    api_key = env["API_KEY"]
    access_key = env["ACCESS_KEY"]

    utc_datetime = datetime.datetime.utcnow()
    utc_datetime.strftime("%Y-%m-%dT %H:%M:%SZ")

    signature = f"{api_key},{access_key},{utc_datetime}"
    signature = signature.encode('utf-8')
    signature = hashlib.sha256(signature)
    signature = signature.hexdigest()

    for category in products_data:  # Categories
        for id in products_data[category]:  # Sku

            provider_sku = products_data[category][id][1]

            product = f'{url}getproduct/?apiKey={api_key}&utcTimeStamp={utc_datetime}&signature={signature}&locale=es&sku={provider_sku}'
            product = requests.get(product).json()

            update_data = {
                "regular_price": str(product["Price"]["UnitPrice"]),
                "stock_quantity": product["InStock"]
            }

            wc.put(f"products/{id}", update_data).json()

    return "success"

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
    
    url = env["INTCOMEX_URL"]
    api_key = env["API_KEY"]
    access_key = env["ACCESS_KEY"]

    utc_datetime = datetime.datetime.utcnow()
    utc_datetime.strftime("%Y-%m-%dT %H:%M:%SZ")

    signature = f"{api_key},{access_key},{utc_datetime}"
    signature = signature.encode('utf-8')
    signature = hashlib.sha256(signature)
    signature = signature.hexdigest()

    for product in new_products:
        
        product = f'{url}getproduct/?apiKey={api_key}&utcTimeStamp={utc_datetime}&signature={signature}&locale=es&sku={new_products[product]}'
        product = requests.get(product).json()

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

    return "success"

@app.route("/intcomex-products")
def intcomex_products():

    url = env["INTCOMEX_URL"]
    api_key = env["API_KEY"]
    access_key = env["ACCESS_KEY"]

    utc_datetime = datetime.datetime.utcnow()
    utc_datetime.strftime("%Y-%m-%dT %H:%M:%SZ")

    signature = f"{api_key},{access_key},{utc_datetime}"
    signature = signature.encode('utf-8')
    signature = hashlib.sha256(signature)
    signature = signature.hexdigest()

    products = f'{url}getcatalog/?apiKey={api_key}&utcTimeStamp={utc_datetime}&signature={signature}&locale=es'
    products = requests.get(products).json()

    return products

if __name__ == '__main__':

    app.run(debug=True, host="0.0.0.0", port=1010)
