from flask import Blueprint, render_template
import json

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
debugging_bp = Blueprint('debugging', __name__)

"""
Visualización de datos ----------------------------------------------------------------------------------------------------
Estas peticiones se utilizan para hacer Debugging y observar datos en formato JSON
"""

@debugging_bp.route('/logs')
def logs():

    with open('logs.json') as f:
        logs_data = json.load(f)

    return logs_data

@debugging_bp.route('/producto/<id>')
def inspeccionar_producto(id):

    return woo.mconsult().get(f"products/{id}").json()  # WooCommerce Product

@debugging_bp.route('/get-categories')
def get_categories():

    categories = woo.mconsult().get(f"products/categories", params={'per_page': 100}).json()

    cats_short = {}
    for category in categories:
        cats_short[str(category['id'])] = str(category["name"])
        
    return cats_short  # WooCommerce Product

@debugging_bp.route("/intcomex-products")
def intcomex_products():

    # return intcomex.get_current_products()

    # return intcomex.get_single_product("MM106NXT69")
    return intcomex.get_current_products()[1]

@debugging_bp.route("/ingram-products")
def ingram_products():

    return ingram.get_products()[0]

@debugging_bp.route("/woo-products")
def wordpress_products():

    # return woo.get_all_prods()

    product = woo.mconsult().get("products", params={'sku': "601009", 'per_page': 1}).json()
    return product

@debugging_bp.route("/woo-imgs")
def wordpress_imgs():

    return woo.get_all_imgs()

@debugging_bp.route("/woocommerce-templates")
def woocommerce_templates():

    return render_template("woocommerce.html")

@debugging_bp.route('/prices')
def prices():

    return ingram.return_all_prices()