from flask import Flask, request, render_template, session, url_for, redirect, send_file
import requests
from dotenv import dotenv_values
import time
from datetime import datetime
import json
import os
import math

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask_mail import Mail, Message

app = Flask(__name__, template_folder='templates', static_folder='static')

# Email SMTP
# Tu dirección de correo electrónico de Gmail y contraseña de aplicación
app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587  # Puerto del servidor SMTP
app.config['MAIL_USERNAME'] = 'mercadeodigital@infotech.com.co'  # Tu dirección de correo electrónico
app.config['MAIL_PASSWORD'] = 'gnyqmrztrmyyjcxn'  # Tu contraseña de aplicación generada para acceso desde apps externas
app.config['MAIL_USE_TLS'] = True  # Habilitar TLS para seguridad
app.config['MAIL_USE_SSL'] = False  # Deshabilitar SSL para TLS

mail = Mail(app)

# Env Vars
env = dotenv_values(".env")

# Local Libs
from local_libs.ingram import ingramConnection
from local_libs.intcomex import intcomexConnection
from local_libs.woocommerce import wooConnection

# Countable Vars
UVT = 47065

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
        print(stock)

        for category in products_data:  # Categories
            for sku in products_data[category]:  # Sku and Prices

                # Ingram part number
                ingram_pnumber = products_data[category][sku]["ingramSku"]
                print(category, "-" , sku, "-", ingram_pnumber)
                
                if sku not in prices:
                    print(f"{sku} not in ingram list")

                # Calculate the final price
                cop_price = int(prices[sku])
                profit = (cop_price * 0.13) + cop_price
                final_price_with_IVA = profit * 1.19

                # Stock
                current_stock_quantity = stock[ingram_pnumber]
                if stock[ingram_pnumber] > 0:
                    stock_status = "instock"
                else:
                    stock_status = "outofstock"

                """
                Teniendo el cuenta la regla de UVT para Celulares y Portatiles
                Segun cierto valor estos dispositivos no llevan IVA
                Entonces el Precio final sera la variable (Profit)
                """
                if category == "smartphones" and (profit < (22*UVT)):
                    final_price_with_IVA = profit
                if category == "laptop" and (profit < (50*UVT)):
                    final_price_with_IVA = profit

                # The final price is rounded
                def round_price(precio):
                    return int(math.ceil(precio / 1000.0)) * 1000

                current_price = final_price_with_IVA  # COP Price
                final_price_with_IVA = round_price(current_price) # The final price is changed

                if (int(final_price_with_IVA) != int(products_data[category][sku]["price"])) or (products_data[category][sku]["stock"] != stock_status) or (products_data[category][sku]["stock_quantity"] != current_stock_quantity):
                    
                    try:
                        # WooCommerce Product
                        product = woo.mconsult().get("products", params={'sku': sku, 'per_page': 1}).json()

                        if product[0]["sale_price"] != "":

                            data = {
                                "regular_price": f"{int(final_price_with_IVA) + 125000}", 
                                "sale_price": f"{int(final_price_with_IVA)}",
                                "stock_status": f"{stock_status}",
                                "manage_stock": True,
                                "stock_quantity": current_stock_quantity
                            }

                        else:

                            data = {
                                "regular_price": f"{int(final_price_with_IVA)}", 
                                "stock_status": f"{stock_status}",
                                "manage_stock": True,
                                "stock_quantity": current_stock_quantity
                            }

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
                        products_data[category][sku]["stock_quantity"] = current_stock_quantity
                        upd_product = json.dumps(products_data, indent=4)

                        with open('ingram_products.json', 'w') as file:
                            file.write(upd_product)
                    except:
                        print("ERROR: Update Ingram Product prices") 

        # Save the Log in "logs.json"
        with open('logs.json') as f:

            logs_data = json.load(f)
            logs_data_list = logs_data["logs"]

            new_log = {
                "date": f"{datetime.now().strftime('%Y-%m-%d')} / {datetime.now().time().strftime('%H:%M:%S')}",
                "type": "Update",
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

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}  # Return success
    else:
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'}

@app.route('/intcomex-update', methods=["POST"])
def intcomex_update():

    if request.method == "POST":

        # Products SKU

        init_time = time.time()
        print(init_time)

        with open('intcomex_products.json') as f:
            products_data = json.load(f)

        # Log data
        qty = 0
        products = []

        # Get the current data of intcomex API
        current_product_data = intcomex.get_current_products()
        print(current_product_data)
        prices = current_product_data[1] # Prices
        stock = current_product_data[2] # Stock

        for category in products_data:  # Categories
            for sku in products_data[category]:  # Sku and Prices

                try:

                    # Icrement
                    increment_percent = 0.13
                    twenty_percent_products = ["101022", "101023", "101024", "101025", "101026", "101027", "101028", "101029", "101030"]
                    if sku in twenty_percent_products:
                        increment_percent = 0.20

                    # Intcomex part number
                    intcomex_sku = products_data[category][sku]["intcomexSku"]
                    
                    # Calculate the final price
                    if intcomex_sku in prices:
                        print(intcomex_sku)
                        cop_price = prices[intcomex_sku]
                        print(cop_price)
                        profit = (cop_price * increment_percent) + cop_price
                        final_price_with_IVA = profit * 1.19
                    else:
                        final_price_with_IVA = products_data[category][sku]["price"]

                    # Stock
                    stock_status = products_data[category][sku]["stock"]
                    current_stock_quantity = stock[intcomex_sku]
                    if intcomex_sku in stock:
                        if stock[intcomex_sku] > 0:
                            stock_status = "instock"
                        else:
                            stock_status = "outofstock"

                    """
                    Teniendo el cuenta la regla de UVT para Celulares y Portatiles
                    Segun cierto valor estos dispositivos no llevan IVA
                    Entonces el Precio final sera la variable (Profit)
                    """
                    if category == "smartphones" and (profit < (22*UVT)):
                        final_price_with_IVA = profit
                    if category == "laptop" and (profit < (50*UVT)):
                        final_price_with_IVA = profit

                    # The final price is rounded
                    def round_price(precio):
                        return int(math.ceil(precio / 1000.0)) * 1000

                    current_price = final_price_with_IVA  # COP Price
                    final_price_with_IVA = round_price(current_price) # The final price is changed

                    if (int(final_price_with_IVA) != int(products_data[category][sku]["price"])) or (products_data[category][sku]["stock"] != stock_status) or (products_data[category][sku]["stock_quantity"] != current_stock_quantity):
                        
                        try:
                            # WooCommerce Product
                            product = woo.mconsult().get("products", params={'sku': sku, 'per_page': 1}).json()

                            if product[0]["sale_price"] != "":

                                data = {
                                    "regular_price": f"{int(final_price_with_IVA) + 125000}", 
                                    "sale_price": f"{int(final_price_with_IVA)}",
                                    "stock_status": f"{stock_status}",
                                    "manage_stock": True,
                                    "stock_quantity": current_stock_quantity
                                }

                            else:

                                data = {
                                    "regular_price": f"{int(final_price_with_IVA)}", 
                                    "stock_status": f"{stock_status}",
                                    "manage_stock": True,
                                    "stock_quantity": current_stock_quantity
                                }

                            woo.mconsult().put(f"products/{product[0]['id']}", data).json()  # Product Update

                            # Log
                            data_log = {
                                "id": product[0]["id"],
                                "sku": f"{sku}",
                                "intcomexsku": intcomex_sku,
                                "stock": stock_status,
                                "past_price": f"{product[0]['price']}",
                                "regular_price": f"{int(final_price_with_IVA)}"
                            }

                            qty += 1
                            products.append(data_log)

                            products_data[category][sku]["price"] = int(final_price_with_IVA)
                            products_data[category][sku]["stock"] = stock_status
                            products_data[category][sku]["stock_quantity"] = current_stock_quantity
                            upd_product = json.dumps(products_data, indent=4)

                            with open('intcomex_products.json', 'w') as file:
                                file.write(upd_product)
                        except:
                            print("ERROR: Update Ingram Product prices") 
                except:
                    print("Ocurrio un error")

        # Save the Log in "logs.json"
        with open('logs.json') as f:

            logs_data = json.load(f)
            logs_data_list = logs_data["logs"]

            new_log = {
                "date": f"{datetime.now().strftime('%Y-%m-%d')} / {datetime.now().time().strftime('%H:%M:%S')}",
                "type": "Update",
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

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}  # Return success
    else:
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'}

@app.route('/add-product', methods=["POST"])
def add_product():

    if request.method == "POST":

        product_sku = request.form["prod_sku"]
        part_num = request.form["prod_pn"]
        category = request.form["category"]
        provider = request.form["provider"]

        try:
            with open(f'{provider}_products.json') as f:
                products_data = json.load(f)

            # Woocommerce product
            woo_prod = woo.get_product_by_sku(product_sku)
            price = woo_prod["regular_price"]
            stock = woo_prod["stock_status"]

            if provider == "ingram":

                new_product = {
                    "ingramSku": part_num,
                    "price": price,
                    "stock": stock
                }

            if provider == "intcomex":

                new_product = {
                    "intcomexSku": part_num,
                    "price": price,
                    "stock": stock
                }

            products_data[category][str(product_sku)] = new_product

            product = json.dumps(products_data, indent=4)

            with open(f'{provider}_products.json', 'w') as f:
                f.write(product)

            # Save the Log in "logs.json"
            with open('logs.json') as f:

                logs_data = json.load(f)
                logs_data_list = logs_data["logs"]

                new_log = {
                    "date": f"{datetime.now().strftime('%Y-%m-%d')} / {datetime.now().time().strftime('%H:%M:%S')}",
                    "type": "Add",
                    "qty": 1,
                    "products": [{
                        "id": woo_prod["id"],
                        "sku": product_sku,
                        "ingrampartnumber": part_num,
                        "stock": stock,
                        "past_price": price,
                        "regular_price": price
                    }]
                }

                logs_data_list.append(new_log)
                logs_data["logs"] = logs_data_list
                log = json.dumps(logs_data, indent=4)

            with open('logs.json', 'w') as file:
                file.write(log)

            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        
        except Exception as ex:

            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)

            return json.dumps({'success':False}), 400, {'ContentType':'application/json'}

@app.route("/update-shipping-clases")
def update_shipping_clases():

    woo_productos = woo.get_all_prods()
    list_product = {product["id"]: {"regular_price": product["regular_price"], "shipping_class": product["shipping_class"]} for product in woo_productos if product["regular_price"] != "" and int(float(product["regular_price"])) < 900000}
    """for product in list_product:
        woo.mconsult().put(f"products/{product}", {"shipping_class": "b-fee"}).json()  # Product Update 
    """
    return list_product

@app.route("/round-up-prices")
def round_up_prices():

    def round_price(precio):
        return int(math.ceil(precio / 1000.0)) * 1000  # Redondear hacia arriba al mil más cercano
    
    # WooCommerce Product
    products = woo.get_all_prods()

    for product in products:

        if product["status"] == "publish":
    
            if product["sale_price"] != "":
                
                print(product["id"])
                print(product["regular_price"])
                print(product["sale_price"])

                current_price = int(product["sale_price"])  # Price in COP
                rounded_price = round_price(current_price)

                print("Precio original:", current_price)
                print("Precio redondeado:", rounded_price)

                if rounded_price <= 100000:
                    increment = 25000
                if rounded_price > 100000:
                    increment = 125000
                if rounded_price > 1000000:
                    increment = 500000

                print(increment)

                data = {
                    "regular_price": f"{int(rounded_price)+increment}", 
                    "sale_price": f"{int(rounded_price)}"
                }

            else:
                print(product["id"])
                print(product["regular_price"])

                current_price = int(product["regular_price"])  # Price in COP
                rounded_price = round_price(current_price)

                print("Precio original:", current_price)
                print("Precio redondeado:", rounded_price)

                data = {
                    "regular_price": f"{int(rounded_price)}"
                }

            woo.mconsult().put(f"products/{product['id']}", data).json()  # Product Update

"""
Data visualization ----------------------------------------------------------------------------------------------------
This functions is used to retrieve information
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
        
    return cats_short  # WooCommerce Product

@app.route("/intcomex-products")
def intcomex_products():

    return intcomex.get_intcomex_prices_list(["ID223XTK11"])

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
# w2ZhZ5W8OYH2Bkzzxbwz