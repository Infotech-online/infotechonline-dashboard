from flask import Blueprint, render_template
import json
import os

# Librerias locales
from local_libs.ingram import ingramConnection
from local_libs.intcomex import intcomexConnection
from local_libs.woocommerce import wooConnection
from local_libs.logs import logRecorder

# Se inicializan las conexiones a las APIs externas (librerias)
ingram = ingramConnection() # Ingram Connection
intcomex = intcomexConnection() # Intcomex Connection
woo = wooConnection() # Woocommerce connection

# Blueprint
debugging_blueprint = Blueprint('debugging', __name__)

# Ruta de la carpeta principal
project_folder = os.path.abspath(os.getcwd())

"""
Visualización de datos ----------------------------------------------------------------------------------------------------
Estas peticiones se utilizan para hacer Debugging y observar datos en formato JSON
"""

@debugging_blueprint.route('/logs')
def logs():

    with open(f'{project_folder}/data/logs.json') as f:
        logs_data = json.load(f)

    return logs_data

@debugging_blueprint.route('/producto/<id>')
def inspeccionar_producto(id):

    return woo.mconsult().get(f"products/{id}").json()  # WooCommerce Product

@debugging_blueprint.route('/get-categories')
def get_categories():

    categories = woo.mconsult().get(f"products/categories", params={'per_page': 100}).json()

    cats_short = {}
    for category in categories:
        cats_short[str(category['id'])] = str(category["name"])
        
    return cats_short  # WooCommerce Product

@debugging_blueprint.route("/intcomex-products")
def intcomex_products():

    # return intcomex.get_current_products()

    # return intcomex.get_single_product("MM106NXT69")
    return intcomex.get_current_products()[1]

@debugging_blueprint.route("/ingram-products")
def ingram_products():

    return ingram.get_products()[0]

@debugging_blueprint.route("/woo-products")
def wordpress_products():

    # return woo.get_all_prods()

    product = woo.mconsult().get("products", params={'sku': "601009", 'per_page': 1}).json()
    return product

@debugging_blueprint.route("/woo-imgs")
def wordpress_imgs():

    return woo.get_all_imgs()

@debugging_blueprint.route("/woocommerce-templates")
def woocommerce_templates():

    return render_template("woocommerce.html")

@debugging_blueprint.route('/prices')
def prices():

    return ingram.return_all_prices()