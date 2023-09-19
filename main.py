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

app = Flask(__name__, template_folder='templates', static_folder='static')

# Env Vars
env = dotenv_values(".env")

# Session vars
app.secret_key = "super secret key"

# WooCommerce API Credentials

wc = API(
    url = env["URL"],
    consumer_key = env['CONSUMER_KEY'],
    consumer_secret = env['CONSUMER_SECRET'],
    version = "wc/v3"
)

@app.route('/submit')
def submit():

    # return render_template("dashboard.html", status_code=r.json())

    # Products SKU
    # Productos a los cuales se les va a cambiar el precio

    with open('products.json') as f:
        products_data = json.load(f)

    # Log data
    qty = 0
    products = []

    # Dollar Price
    request_currencies = requests.get("http://apilayer.net/api/live?access_key=35fecb58061d2dcd76ce985b306bcc07&currencies=COP&source=USD&format=1")
    response = request_currencies.json()

    for category in products_data: # Categories
        for sku in products_data[category]: # Sku and Prices

            product_dollar_price = products_data[category][sku]
            usd_to_cop = response["quotes"]["USDCOP"] # This var is set in env file

            # Calc the final price
            cop_price = float(product_dollar_price) * float(usd_to_cop)
            profit = (cop_price * 0.13) + cop_price
            final_price_with_IVA =  profit * 1.19

            product = wc.get("products", params={'sku': sku, 'per_page': 100}).json() # WooCommerce Product

            data = {"regular_price": f"{int(final_price_with_IVA)}"}
            wc.put(f"products/{product[0]['id']}", data).json() # Product Update

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

    # Save a Log in "logs.json"
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

    return "success" # Return success

@app.route('/logs')
def logs():

    with open('logs.json') as f:
        logs_data = json.load(f)

    return logs_data

@app.route('/')
def dashboard():

    products = wc.get("products", params={'per_page': 100}).json() # WooCommerce Productproducts
    with open('logs.json') as f:
        logs_data = json.load(f)

    # Dollar Price
    request_currencies = requests.get("http://apilayer.net/api/live?access_key=35fecb58061d2dcd76ce985b306bcc07&currencies=COP&source=USD&format=1")
    response = request_currencies.json()
    dollar = response["quotes"]["USDCOP"]

    return render_template("dashboard.html", products=products, qty=len(products), logs=logs_data, dollar=dollar)

if __name__ == '__main__':

    app.run(debug=True, host="0.0.0.0")