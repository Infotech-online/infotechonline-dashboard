from flask import Blueprint, request, current_app
import time
import json
import os
import math
import random

# Librerias locales
from local_libs.ingram import ingramConnection
from local_libs.intcomex import intcomexConnection
from local_libs.woocommerce_api import wooConnection
from local_libs.logs import logRecorder

# Se inicializan las conexiones a las APIs externas (librerias)
ingram = ingramConnection() # Ingram Connection
intcomex = intcomexConnection() # Intcomex Connection
woo = wooConnection() # Woocommerce connection

# Blueprint
price_increase_blueprint = Blueprint('price_increase_blueprint', __name__)

@price_increase_blueprint.route('/increment-list')
def increment_with_shipping_fee():

    """
    Los precios de la tienda estan con un margen de 13% pero se van a subir segun las
    siguientes reglas:

    Productos menores a 1.500.000 tendran el 20% y 15.000 de valor del envio incluido
    dentro del precio final del producto.

    Productos mayores a 1.500.000 tendram el 13% y 1% de valor del envio incluidos dentro
    del precio final del producto
    """

    # Se carga el contexto de la aplicación de Flask
    with current_app.app_context():

        # Variables de reglas contables

        """
        Esta variable define el valor de los UVTs manejados en Colombia.
        Algunos productos estan excentos de IVA como los Portatiles y Celulares.

        Este tipo de productos estan excentos de IVA hasta cierto valor de UVT por
        eso este valor es una constante hasta que se registre un nuevo valor el
        proximo año.
        """

        # Código que utiliza current_app
        UVT = current_app.config["UVT"]
        project_folder = current_app.config["PROJECT_FOLDER"]

    # Se guarda el registro dentro de "logs.json"
    with open(f'{project_folder}/data/product_prices_02.json') as f:
        last_products_data = json.load(f)

    # Se obtienen todos los productos de woocommerce
    all_products = woo.get_all_prods(1)

    # Por cada producto en la tienda
    for product in all_products:

        # Si el producto se encuentra publicado
        if product["status"] == "publish":

            UVT_rule = False
            UVT_quantity = 0
            profit_margin = 0.15
            decrease = 0.87

            regular_price = product["regular_price"]
            sale_price = product["sale_price"]

            product_price = regular_price if sale_price == "" else sale_price
            product_price = int(product_price)

            # Por cada categoria encontrar las que tienen variaciones en cuanto a reglas de precios
            for category in product["categories"]:

                if category["name"] == "Portatiles":
                    UVT_rule = True
                    UVT_quantity = 50

                if category["name"] == "Celulares" or category["name"] == "Tablets":
                    UVT_rule = True
                    UVT_quantity = 22

                """if category["name"] == "Celulares" or category["name"] == "Hogar Inteligente":
                    profit_margin = 0.15"""

            if UVT_rule and product_price < (UVT_quantity * UVT):

                if last_products_data[product["sku"]]["shipping_type"] == "A: 15.000":
                    product_price_base = product_price - 15000

                if last_products_data[product["sku"]]["shipping_type"] == "B: 1%":
                    print("encontrado", product_price)
                    product_price_base = product_price * 0.99

                if product_price_base <= 1500000:
                    decrease = 0.8
                if product_price_base > 1500000:
                    decrease = 0.87

                base_price = product_price_base * decrease # Se le resta el porcentaje anterior
                
                if product["sku"] == "401043 - C3VHY":
                    print("\n", product_price_base, base_price)

                profit_margin = 0.13 if base_price > 1500000 else profit_margin
                product_price = base_price / (1 - profit_margin)

                # Se añade el valor del envio antes de IVA
                if product_price <= 1500000:
                    shipping_type = "A: 15.000"
                    product_price += 15000

                if product_price > 1500000:
                    shipping_type = "B: 1%"
                    product_price = product_price / (1 - 0.01)

                # Si con el precio nuevo supera los UVT entonces se le añade IVA
                product_price = product_price * 1.19 if product_price > (UVT_quantity * UVT) else product_price
                iva_state = "included" if product_price > (UVT_quantity * UVT) else "excluded"

                # Se redondean los precios 1000 pesos por encima
                final_price = int(math.ceil(product_price / 1000.0)) * 1000 # (REDONDEADO)

                print(f"{product['sku']} / {final_price} / 1 NO IVA")

            if (UVT_rule and product_price > (UVT_quantity * UVT)) or UVT_rule == False:

                product_price_base = product_price / 1.19 # Se quita el IVA

                if last_products_data[product["sku"]]["shipping_type"] == "A: 15.000":
                    product_price_base -= 15000
                if last_products_data[product["sku"]]["shipping_type"] == "B: 1%":
                    product_price_base = product_price_base * 0.99

                if product_price_base <= 1500000:
                    decrease = 0.8
                if product_price_base > 1500000:
                    decrease = 0.87

                base_price = product_price_base * decrease # Se le resta el porcentaje con la formula anterior

                profit_margin = 0.13 if base_price > 1500000 else profit_margin
                product_price = base_price / (1 - profit_margin) # Se añade el porcentaje con la nueva formula

                # Se añade el valor del envio antes de IVA
                if product_price <= 1500000:
                    shipping_type = "A: 15.000"
                    product_price += 15000

                if product_price > 1500000:
                    shipping_type = "B: 1%"
                    product_price = product_price / (1 - 0.01)

                product_price = product_price * 1.19 # Se añade el IVA

                iva_state = "included"
                
                # Se redondean los precios 1000 pesos por encima
                final_price = int(math.ceil(product_price / 1000.0)) * 1000 # (REDONDEADO)

                print(f"{product['sku']} / {final_price} / 2 CON IVA")

            # Definir que tipo de precio es (oferta o precio normal)
            if sale_price == "": 

                new_regular_price = final_price
                new_sale_price = ""
                discount_rate = 0
                on_sale = False

                # Totos los productos tendran envio gratuito
                shipping_class = "free-fee"
                shipping_class_id = 1781

            else:

                # Si el producto esta en oferta
                on_sale = True
                sale_price = int(sale_price)

                # Seleccionar un porcentaje de descuento
                # Generar un descuento aleatorio entre 10% y 50%
                opciones = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
                discount = random.choice(opciones)

                # Convertir el descuento a porcentaje y redondearlo a dos decimales
                discount_rate = discount * 100

                new_sale_price = final_price

                # Totos los productos tendran envio gratuito
                shipping_class = "free-fee"
                shipping_class_id = 1781

                new_regular_price = final_price * (1 + discount)
                new_regular_price = int(math.ceil(new_regular_price / 1000.0)) * 1000

            # Se guarda el registro dentro de "logs.json"
            with open(f'{project_folder}/data/product_prices_05.json') as f:

                logs_data = json.load(f)
                logs_data_list = logs_data

                if iva_state == "included":
                    tax_status = "taxable"
                if iva_state == "excluded":
                    tax_status = "shipping"

                # Estructura del Log de tipo "Add"
                logs_data[product['sku']] = {
                    "id": product['id'],
                    "image": product["images"][0]["src"],
                    "regular_price": int(regular_price),
                    "sale_price": sale_price,
                    "new_regular_price": new_regular_price,
                    "new_sale_price": new_sale_price,
                    "base_price": int(math.ceil(base_price / 1000.0)) * 1000,
                    "profit_margin": profit_margin,
                    "IVA": iva_state,
                    "on_sale": on_sale,
                    "discount_rate": discount_rate,
                    "tax_status": tax_status,
                    "shipping_class": shipping_class,
                    "shipping_class_id": shipping_class_id,
                    "shipping_type": shipping_type,
                    "categories": product["categories"]
                }

                logs_data = logs_data_list
                log = json.dumps(logs_data, indent=4)

            # Se escribe el nuevo Log
            with open(f'{project_folder}/data/product_prices_05.json', 'w') as file:
                file.write(log)

    with open(f'{project_folder}/data/product_prices_05.json') as f:
        logs_data = json.load(f)

    return logs_data

@price_increase_blueprint.route('/get-increment-list')
def price_profit_correction():

    """
    Los precios de la tienda estan con un margen del 13% pero se quieren subir todos
    al 15%, hay algunas excepciones como que los productos pequeños o accesorios van
    van a incrementar al 20%, tambien se tiene que tener en cuenta el valor del UVT
    para portatiles, celulares y tablets (50 UVT y 22 UVT).
    
    La nueva formula de ganancia es: precio / (1-13)
    13 es el porcentaje de ganancia
    """

    # Se carga el contexto de la aplicación de Flask
    with current_app.app_context():

        # Variables de reglas contables

        """
        Esta variable define el valor de los UVTs manejados en Colombia.
        Algunos productos estan excentos de IVA como los Portatiles y Celulares.

        Este tipo de productos estan excentos de IVA hasta cierto valor de UVT por
        eso este valor es una constante hasta que se registre un nuevo valor el
        proximo año.
        """

        # Código que utiliza current_app
        UVT = current_app.config["UVT"]
        project_folder = current_app.config["PROJECT_FOLDER"]

    # Se obtienen todos los productos de woocommerce
    all_products = woo.get_all_prods(1)

    # Por cada producto en la tienda
    for product in all_products:

        # Si el producto se encuentra publicado en la tienda
        if product["status"] == "publish":

            """
            50 UVT = 2.335.250
            22 UVT = 1.035.430
            """
            UVT_rule = False
            UVT_quantity = 0
            profit_margin = 0.13

            regular_price = product["regular_price"]
            sale_price = product["sale_price"]

            product_price = regular_price if sale_price == "" else sale_price
            product_price = int(product_price)

            # Por cada categoria encontrar las que tienen variaciones en cuanto a reglas de precios
            for category in product["categories"]:

                if category["name"] == "Accesorios":
                    # Si el producto es un accesorio y su precio es menor a 500.000
                    if product_price < 200000:
                        profit_margin = 0.20

                if category["name"] == "Portatiles":
                    UVT_rule = True
                    UVT_quantity = 50
                if category["name"] == "Celulares" or category["name"] == "Tablets":
                    UVT_rule = True
                    UVT_quantity = 22

            if UVT_rule and product_price < (UVT_quantity * UVT):

                base_price = product_price / 1.13 # Se le resta el porcentaje anterior
                product_price = base_price / (1 - profit_margin)

                # Si con el precio nuevo supera los 22 UVT entonces se le añade IVA
                product_price = product_price * 1.19 if product_price > (UVT_quantity * UVT) else product_price
                iva_state = "included" if product_price > (UVT_quantity * UVT) else "excluded"

                # Se redondean los precios 1000 pesos por encima
                final_price = int(math.ceil(product_price / 1000.0)) * 1000 # (REDONDEADO)

                print(f"{product['sku']} / {final_price} / 1 NO IVA")

            if UVT_rule and product_price > (UVT_quantity * UVT):

                product_price = product_price / 1.19 # Se quita el IVA
                base_price = product_price / 1.13 # Se le resta el porcentaje con la formula anterior
                product_price = base_price / (1 - profit_margin) # Se añade el porcentaje con la nueva formula

                product_price = product_price * 1.19 # Se añade el IVA

                iva_state = "included"
                
                # Se redondean los precios 1000 pesos por encima
                final_price = int(math.ceil(product_price / 1000.0)) * 1000 # (REDONDEADO)

                print(f"{product['sku']} / {final_price} / 2 CON IVA")

            if UVT_rule == False:

                product_price = product_price / 1.19 # Se quita el IVA
                base_price = product_price / 1.13 # Se le resta el porcentaje con la formula anterior
                product_price = base_price / (1 - profit_margin) # Se añade el porcentaje con la nueva formula

                product_price = product_price * 1.19 # Se añade el IVA

                iva_state = "included"
                
                # Se redondean los precios 1000 pesos por encima
                final_price = int(math.ceil(product_price / 1000.0)) * 1000 # (REDONDEADO)

                print(f"{product['sku']} --- {product['id']} / / {final_price} / 3 SIN REGLA")

            # Definir que tipo de precio es (oferta o precio normal)
            if sale_price == "": 
                new_regular_price = final_price
                new_sale_price = ""
                discount_rate = 0
                on_sale = False

                if new_regular_price > 900000:
                    shipping_class = "b-fee"
                    shipping_class_id = 1611
                else:
                    shipping_class = "a-fee"
                    shipping_class_id = 1610
            else:

                # Si el producto esta en oferta
                on_sale = True
                sale_price = int(sale_price)                

                # Seleccionar un porcentaje de descuento
                # Generar un descuento aleatorio entre 10% y 50%
                opciones = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
                discount = random.choice(opciones)

                # Convertir el descuento a porcentaje y redondearlo a dos decimales
                discount_rate = discount * 100

                new_sale_price = final_price

                if new_sale_price > 900000:
                    shipping_class = "b-fee"
                    shipping_class_id = 1611
                else:
                    shipping_class = "a-fee"
                    shipping_class_id = 1610

                new_regular_price = final_price * (1 + discount)
                new_regular_price = int(math.ceil(new_regular_price / 1000.0)) * 1000

            # Se guarda el registro dentro de "logs.json"
            with open(f'{project_folder}/data/product_prices.json') as f:

                logs_data = json.load(f)
                logs_data_list = logs_data

                if iva_state == "included":
                    tax_status = "taxable"
                if iva_state == "excluded":
                    tax_status = "shipping"

                # Estructura del Log de tipo "Add"
                logs_data[product['sku']] = {
                    "id": product['id'],
                    "image": product["images"][0]["src"],
                    "regular_price": int(regular_price),
                    "sale_price": sale_price,
                    "new_regular_price": new_regular_price,
                    "new_sale_price": new_sale_price,
                    "base_price": int(math.ceil(base_price / 1000.0)) * 1000,
                    "profit_margin": profit_margin,
                    "IVA": iva_state,
                    "on_sale": on_sale,
                    "discount_rate": discount_rate,
                    "tax_status": tax_status,
                    "shipping_class": shipping_class,
                    "shipping_class_id": shipping_class_id
                }

                logs_data = logs_data_list
                log = json.dumps(logs_data, indent=4)

            # Se escribe el nuevo Log
            with open(f'{project_folder}/data/product_prices.json', 'w') as file:
                file.write(log)

    with open(f'{project_folder}/data/product_prices.json') as f:
        logs_data = json.load(f)

    return logs_data

@price_increase_blueprint.route('/update-with-increment-list')
def update_with_increment_list():

    # Se carga el contexto de la aplicación de Flask
    with current_app.app_context():

        project_folder = current_app.config["PROJECT_FOLDER"]

    # Se guarda el registro dentro de "logs.json"
    with open(f'{project_folder}/data/product_prices_05.json') as f:

        logs_data = json.load(f)
        product_list = logs_data

    # Por cada producto en la tienda
    for product_sku in product_list:
        
        product = product_list[product_sku]

        print(f"{product_sku} - iniciando")

        data = {
            "regular_price": f"{product['new_regular_price']}", 
            "sale_price": f"{product['new_sale_price']}",
            "tax_status": product['tax_status'],
            "shipping_class": product['shipping_class'],
            "shipping_class_id": int(product['shipping_class_id'])
        }

        # Se realiza una consulta de tipo PUT a Woocommerce para actualizar los valores de los productos actualizados
        woo.mconsult().put(f"products/{product['id']}", data).json()

        print("- finalizado")

    return "finished"

# Redondear precios de los productos
@price_increase_blueprint.route("/round-up-prices")
def round_up_prices():

    """
    Por ejemplo:
    Si el precio final del producto queda en 1.300.700
    esta función lo redondea a 1.301.000
    (1.000 pesos) sin importar la cantidad de cifras en las centenas
    """

    def round_price(precio):
        return int(math.ceil(precio / 1000.0)) * 1000  # Redondear hacia arriba al mil más cercano
    
    # Obtener todos los productos de Woocommerce
    products = woo.get_all_prods()

    # Por cada producto dentro del listado de productos    
    for product in products:
        
        # Si el producto se encuentra publicado en la tienda
        if product["status"] == "publish":
            
            # Si el producto esta en descuento
            if product["sale_price"] != "":
                
                print(product["id"])
                print(product["regular_price"])
                print(product["sale_price"])

                # Se redondea el valor de "sale_price" (precio de oferta)
                current_price = int(product["sale_price"])
                rounded_price = round_price(current_price) # Valor redondeado

                print("Precio original:", current_price)
                print("Precio redondeado:", rounded_price)

                """
                El valor de "regular_price" debe ser mayor a "sale_price"

                Por lo tanto, este es un incremento fijo que dependiendo del valor
                del producto sera una cantidad:

                Si el precio es menor o igual a 100.000 el incremento sera de 25.000
                Si el precio es mayor a 100.000 el incremento sera de 125.000
                Si el precio es mayor a 1.000.000 el incremento sera de 500.000

                Este valor es unicamente para hacer ver que el producto antes de oferta
                estaba mas caro que su precio original (estos valores pueden o no ser veridicos)
                """

                if rounded_price <= 100000:
                    increment = 25000
                if rounded_price > 100000:
                    increment = 125000
                if rounded_price > 1000000:
                    increment = 500000

                # Se agregan los datos del nuevo precio del producto
                data = {
                    "regular_price": f"{int(rounded_price)+increment}", 
                    "sale_price": f"{int(rounded_price)}"
                }

            else:

                # Si el producto no esta en descuento

                print(product["id"])
                print(product["regular_price"])

                # Se redondea el precio en "regular_price"
                current_price = int(product["regular_price"])  # Price in COP
                rounded_price = round_price(current_price)

                print("Precio original:", current_price)
                print("Precio redondeado:", rounded_price)

                # Se agregan los datos del nuevo precio del producto
                data = {
                    "regular_price": f"{int(rounded_price)}"
                }

            # Se actualiza la información del producto en la tienda
            woo.mconsult().put(f"products/{product['id']}", data).json()  # Product Update