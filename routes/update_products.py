from flask import Blueprint, request
import time
import json
import os
import math
import random

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
update_products_blueprint = Blueprint('update_products_blueprint', __name__)

# Variables de reglas contables

"""
Esta variable define el valor de los UVTs manejados en Colombia.
Algunos productos estan excentos de IVA como los Portatiles y Celulares.

Este tipo de productos estan excentos de IVA hasta cierto valor de UVT por
eso este valor es una constante hasta que se registre un nuevo valor el
proximo año.
"""
UVT = 47065 # Valor del UVT (Año 2024)

# Ruta de la carpeta principal
project_folder = os.path.abspath(os.getcwd())

# Añadir o enlazar un nuevo producto a la base de datos local (archivos JSON)
@update_products_blueprint.route('/add-product', methods=["POST"])
def add_product():

    """
    Se agrega un nuevo producto dentro de las estructuras JSON como:
    "ingram_products.json" e "intcomex_products.json"
    Tambien se crea un nuevo registro de tipo "Add"
    """

    # Si la petición es de tipo POST
    if request.method == "POST":
        
        # Se obtienen los datos de la petición
        product_sku = request.form["prod_sku"]
        part_num = request.form["prod_pn"]
        category = request.form["category"]
        provider = request.form["provider"]

        # Se inicializa el modulo de registros
        logs = logRecorder()

        try:

            # Se abre el archivo de los productos del proveedor
            with open(f'{project_folder}/data/{provider}_products.json') as f:
                products_data = json.load(f)

            # Se obtiene el producto de Woocommerce
            woo_prod = woo.get_product_by_sku(str(product_sku))

            # Se obtiene el precio del producto
            price = woo_prod["regular_price"]
            # Se obtiene el stock del producto
            stock = woo_prod["stock_status"]

            # Si el proveedor es Ingram
            if provider == "ingram":
                
                # La estructura del producto sera:
                new_product = {
                    "ingramSku": part_num,
                    "price": price,
                    "stock": stock,
                    "availability": True,
                    "stock_quantity": 0
                }

            # Si el proveedor es Intcomex
            if provider == "intcomex":
                
                # La estructura del producto sera:
                new_product = {
                    "intcomexSku": part_num,
                    "price": price,
                    "stock": stock,
                    "availability": True,
                    "stock_quantity": 0
                }

            # Se añade el nuevo producto a la categoría seleccionada
            products_data[category][product_sku] = new_product

            # Se agrega el nuevo producto dentro del archivo
            product = json.dumps(products_data, indent=4)

            # Se escriben los cambios
            with open(f'{project_folder}/data/{provider}_products.json', 'w') as f:
                f.write(product)

            # Se guarda el registro dentro de "logs.json"
            logs.add_new_product_log(woo_prod["id"], product_sku, part_num, stock, price)

            # Se retorna un mensaje de tipo Success
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        
        except Exception as ex:

            # Si no se pudo realizar el proceso

            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)

            # Se retorna un mensaje negativo
            return json.dumps({'success':False}), 400, {'ContentType':'application/json'}

# Actualizar los precios de los productos de Ingram
@update_products_blueprint.route('/ingram-update', methods=["POST"])
def ingram_update():

    """
    Se actualizan todos los productos enlazados que tengan como proveedor a Ingram
    """

    # Si la petición es de tipo POST
    if request.method == "POST":
        
        # Se imprime el tiempo de inicio
        init_time = time.time()
        print(init_time)

        # Se abre el archivo "ingram_products.json"
        with open(f'{project_folder}/data/ingram_products.json') as f:
            products_data = json.load(f)

        # Datos del nuevo Log o registro de la actualización
        qty = 0
        products = []

        # Listado de precios de Ingram
        prices = ingram.return_all_prices()

        # Listado de stock de Ingram
        stock = ingram.return_all_stock()

        # Se inicializa el modulo de registros
        logs = logRecorder()

        # Por cada categoría dentro del archivo "ingram_products.json"
        for category in products_data:  # Categories
            # Por cada SKU dentro de la categoría
            for sku in products_data[category]:  # Sku and Prices

                # Se ontiene el numero de parte del producto (Ingram)
                ingram_pnumber = products_data[category][sku]["ingramSku"]
                # print(category, "-" , sku, "-", ingram_pnumber)

                # Se calcula el precio final del producto

                base_price = int(prices[ingram_pnumber]) # Precio base del mayorista
                iva_state = "taxable" # Estado de IVA del producto

                profit_margin = 0.13

                if category == "accesorios":

                    # Si el producto es un accesorio y su precio base es menor a 200.000
                    if base_price < 200000:
                        profit_margin = 0.20

                """
                La formula es: 
                incremento = Precio del producto / (1 - margen de ganancia)
                valor final = incremento * 1.19
                """
                profit = base_price / (1 - profit_margin)
                final_price = profit * 1.19

                # Se obtiene el stock actual del producto
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
                if (category == "smartphones" and (profit < (22*UVT))) or (category == "laptop" and (profit < (50*UVT))):

                    final_price = profit
                    iva_state = "shipping" # Excluido de IVA

                # El precio final del producto se redondea
                """
                Por ejemplo:
                Si el precio final del producto queda en 1.300.700
                esta función lo redondea a 1.301.000
                (1.000 pesos) sin importar la cantidad de cifras en las centenas
                """

                final_price = int(math.ceil(final_price / 1000.0)) * 1000  # Precio actual con IVA (REDONDEADO)

                # Si el producto cambio de precio o stock, se actualizaran los valores dentro de la tienda
                if (int(final_price) != int(products_data[category][sku]["price"])) or (products_data[category][sku]["stock"] != stock_status) or (products_data[category][sku]["stock_quantity"] != current_stock_quantity):
                    
                    try:
                        # Consulta para obtener el producto de WooCommerce
                        product = woo.mconsult().get("products", params={'sku': sku, 'per_page': 1}).json()

                        last_stock_quantity = product[0]["stock_quantity"]

                        if product[0]["sale_price"] != "":

                            # Si el producto esta en oferta
                            # Se agrega el valor "sale_price"
                            # El valor de "regular_price" debe ser mayor a "sale_price"
                            sale_price = int(sale_price)

                            # Seleccionar un porcentaje de descuento
                            # Generar un descuento aleatorio entre 10% y 50%
                            opciones = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
                            discount = random.choice(opciones)

                            new_sale_price = final_price

                            if new_sale_price > 900000:
                                shipping_class = "b-fee"
                                shipping_class_id = 1611
                            else:
                                shipping_class = "a-fee"
                                shipping_class_id = 1610

                            new_regular_price = final_price * (1 + discount)
                            new_regular_price = int(math.ceil(new_regular_price / 1000.0)) * 1000

                            data = {
                                "regular_price": f"{int(new_regular_price)}", 
                                "sale_price": f"{int(new_sale_price)}",
                                "stock_status": f"{stock_status}",
                                "manage_stock": True,
                                "stock_quantity": current_stock_quantity,
                                "tax_status": iva_state,
                                "shipping_class": shipping_class,
                                "shipping_class_id": int(shipping_class_id)
                            }

                        else:

                            # Si el producto no esta en oferta
                            # Se cambia unicamente el valor "regular_price"

                            new_regular_price = final_price
                            new_sale_price = ""

                            if new_regular_price > 900000:
                                shipping_class = "b-fee"
                                shipping_class_id = 1611
                            else:
                                shipping_class = "a-fee"
                                shipping_class_id = 1610                            

                            data = {
                                "regular_price": f"{int(new_regular_price)}", 
                                "stock_status": f"{stock_status}",
                                "manage_stock": True,
                                "stock_quantity": current_stock_quantity,
                                "tax_status": iva_state,
                                "shipping_class": shipping_class,
                                "shipping_class_id": int(shipping_class_id)
                            }

                        # Se realiza una consulta de tipo PUT a Woocommerce para actualizar los valores de los productos actualizados
                        woo.mconsult().put(f"products/{product[0]['id']}", data).json()

                        # Se añade un nuevo producto al nuevo registro
                        logs.add_product_to_update_log(product[0]["id"], sku, ingram_pnumber, stock_status, last_stock_quantity, current_stock_quantity, product[0]['price'], final_price, "ingram", "success")

                        # Se cambian los datos del producto dentro de "ingram_products.json"
                        # Para futuras actualizaciones
                        products_data[category][sku]["price"] = int(final_price)
                        products_data[category][sku]["stock"] = stock_status
                        products_data[category][sku]["stock_quantity"] = current_stock_quantity
                        upd_product = json.dumps(products_data, indent=4)

                        # Se escriben los cambios dentro de "ingram_products.json"
                        with open(f'{project_folder}/data/ingram_products.json', 'w') as file:
                            file.write(upd_product)
                    except:

                        print(sku)
                        product = woo.mconsult().get("products", params={'sku': sku, 'per_page': 1}).json()
                        last_stock_quantity = product[0]["stock_quantity"]

                        # Se añade un nuevo producto al nuevo registro
                        logs.add_product_to_update_log(product[0]["id"], sku, ingram_pnumber, stock_status, last_stock_quantity, current_stock_quantity, product[0]['price'], final_price, "ingram", "error")
                        # Si no se pudo realizar la actualización
                        print("ERROR: Update Ingram Product prices") 

        # Se guarda y escribe el nuevo registro de actualización
        logs.add_new_update_log()

        # Se imprime el tiempo total que tomo el proceso
        end_time = time.time()
        total_time = end_time - init_time
        print(total_time)

        # Se retorna un mensaje de Success
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}  # Return success
    else:

        # Si salio mal el proceso se retorna un mensaje de error
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'}

# Actualizar los precios de los productos de Ingram
@update_products_blueprint.route('/intcomex-update', methods=["POST"])
def intcomex_update():

    """
    Se actualizan todos los productos enlazados que tengan como proveedor a Intcomex
    """

    # Si la petición es de tipo POST
    if request.method == "POST":
        
        # Se imprime el tiempo de inicio
        init_time = time.time()
        print(init_time)

        # Se abre el archivo "intcomex_products.json"
        with open(f'{project_folder}/data/intcomex_products.json') as f:
            products_data = json.load(f)

        # Se inicializan las variables que almacenaran los datos de los registros o Logs
        qty = 0
        products = []

        # Obtener todos los  productos actuales de Intcomes
        current_product_data = intcomex.get_current_products()

        # Se obtienen todos los precios
        prices = current_product_data[1] # Prices

        # Se obtienen todos los valores de stock
        stock = current_product_data[2] # Stock

        # Se inicializa el modulo de registros
        logs = logRecorder()

        # Por cada categoría dentro de "intcomex_products.json"
        for category in products_data:  # Categories
            # Por cada SKU dentro de la categoría
            for sku in products_data[category]:  # Sku and Prices

                # Se obtiene el numero de parte de Intcomex
                intcomex_sku = products_data[category][sku]["intcomexSku"]
                
                # Se calcula el precio final del producto

                iva_state = "taxable" # Estado de IVA del producto

                if intcomex_sku in prices and intcomex_sku in stock:

                    base_price = int(prices[intcomex_sku]) # Precio base del mayorista

                    profit_margin = 0.13

                    if category == "accesorios":

                        # Si el producto es un accesorio y su precio base es menor a 200.000
                        if base_price < 200000:
                            profit_margin = 0.20

                    """
                    La formula es: 
                    incremento = Precio del producto / (1 - margen de ganancia)
                    valor final = incremento * 1.19
                    """
                    profit = base_price / (1 - profit_margin)
                    final_price = profit * 1.19

                    stock_status = products_data[category][sku]["stock"]

                    # La catidad de stock se almacenara en "current_stock_quantity"
                    current_stock_quantity = stock[intcomex_sku]

                    # Si el stock es mayor a 0 el estado sera "instock"
                    if stock[intcomex_sku] > 0:
                        stock_status = "instock"
                    else:
                        stock_status = "outofstock"

                    """
                    Teniendo el cuenta la regla de UVT para Celulares y Portatiles
                    Segun cierto valor estos dispositivos no llevan IVA
                    Entonces el Precio final sera la variable (Profit)
                    """
                    if (category == "smartphones" and (profit < (22*UVT))) or (category == "laptop" and (profit < (50*UVT))):

                        final_price = profit
                        iva_state = "shipping"

                    # El precio final del producto se redondea
                    """
                    Por ejemplo:
                    Si el precio final del producto queda en 1.300.700
                    esta función lo redondea a 1.301.000
                    (1.000 pesos) sin importar la cantidad de cifras en las centenas
                    """

                    final_price = int(math.ceil(final_price / 1000.0)) * 1000 # Precio actual con IVA (REDONDEADO)

                else:

                    # final_price_with_IVA = products_data[category][sku]["price"]
                    print(f"Producto no se encuentra en el listado de precios {intcomex_sku}")

                # if (int(final_price_with_IVA) != int(products_data[category][sku]["price"])) or (products_data[category][sku]["stock"] != stock_status) or (products_data[category][sku]["stock_quantity"] != current_stock_quantity):
                if intcomex_sku in prices and intcomex_sku in stock:
                    
                    # Consulta para obtener el producto de WooCommerce
                    product = woo.mconsult().get("products", params={'sku': sku, 'per_page': 1}).json()

                    # Obtener el stock del producto actual en la tienda
                    last_stock_quantity = product[0]["stock_quantity"]

                    # Si el producto esta en oferta
                    if product[0]["sale_price"] != "":

                        # Si el producto esta en oferta
                        # Se agrega el valor "sale_price"
                        # El valor de "regular_price" debe ser mayor a "sale_price"

                        # Seleccionar un porcentaje de descuento
                        # Generar un descuento aleatorio entre 10% y 40%
                        opciones = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
                        discount = random.choice(opciones)

                        new_sale_price = final_price

                        if new_sale_price > 900000:
                            shipping_class = "b-fee"
                            shipping_class_id = 1611
                        else:
                            shipping_class = "a-fee"
                            shipping_class_id = 1610

                        new_regular_price = final_price * (1 + discount)
                        new_regular_price = int(math.ceil(new_regular_price / 1000.0)) * 1000

                        data = {
                            "regular_price": f"{int(new_regular_price)}", 
                            "sale_price": f"{int(new_sale_price)}",
                            "stock_status": f"{stock_status}",
                            "manage_stock": True,
                            "stock_quantity": current_stock_quantity,
                            "tax_status": iva_state,
                            "shipping_class": shipping_class,
                            "shipping_class_id": int(shipping_class_id)
                        }

                    else:

                        # Si el producto no esta en oferta
                        # Se cambia unicamente el valor "regular_price"

                        new_regular_price = final_price
                        new_sale_price = ""

                        if new_regular_price > 900000:
                            shipping_class = "b-fee"
                            shipping_class_id = 1611
                        else:
                            shipping_class = "a-fee"
                            shipping_class_id = 1610            

                            # Si el producto no esta en oferta
                            # Se cambia unicamente el valor "regular_price"

                            new_regular_price = final_price
                            new_sale_price = ""

                            if new_regular_price > 900000:
                                shipping_class = "b-fee"
                                shipping_class_id = 1611
                            else:
                                shipping_class = "a-fee"
                                shipping_class_id = 1610            

                            data = {
                                "regular_price": f"{int(new_regular_price)}", 
                                "stock_status": f"{stock_status}",
                                "manage_stock": True,
                                "stock_quantity": current_stock_quantity,
                                "tax_status": iva_state,
                                "shipping_class": shipping_class,
                                "shipping_class_id": int(shipping_class_id)
                            }

                    # Se actualiza el producto dentro de la tienda
                    woo.mconsult().put(f"products/{product[0]['id']}", data).json()

                    # Se añade un nuevo producto al nuevo registro
                    logs.add_product_to_update_log(product[0]["id"], sku, intcomex_sku, stock_status, last_stock_quantity, current_stock_quantity, product[0]['price'], final_price, "intcomex", "success")

                    # Se cambian los datos del producto dentro de "ingram_products.json"
                    # Para futuras actualizaciones
                    products_data[category][sku]["price"] = int(final_price)
                    products_data[category][sku]["stock"] = stock_status
                    products_data[category][sku]["stock_quantity"] = current_stock_quantity
                    upd_product = json.dumps(products_data, indent=4)

                    # Se escriben los cambios dentro de "intcomex_products.json"
                    with open(f'{project_folder}/data/intcomex_products.json', 'w') as file:
                        file.write(upd_product)

                else:

                    # Si no se pudo realizar la actualización

                    # Obtener los detalles del producto de Woocommerce
                    product = woo.mconsult().get("products", params={'sku': sku, 'per_page': 1}).json()

                    # Obtener la cantidad actual de stock del producto en la tienda
                    last_stock_quantity = product[0]["stock_quantity"]

                    # Registrar el producto con error
                    logs.add_product_to_update_log(product[0]["id"], sku, intcomex_sku, "outofstock", last_stock_quantity, 0, product[0]['price'], None, "intcomex", "error")                    

                    # Se establece el producto con stock en 0
                    data = {
                        "manage_stock": True,
                        "stock_quantity": 0
                    }

                    # Se actualiza el producto dentro de la tienda
                    woo.mconsult().put(f"products/{product[0]['id']}", data).json()  # Product Update

                    print(f"Ocurrio un error con el producto {product[0]['id']}")

        # Se guardan los registros dentro de "logs.json"
        logs.add_new_update_log()

        # Se imprime el tiempo total que tomo el proceso
        end_time = time.time()
        total_time = end_time - init_time
        print(total_time)

        # Se retorna un mensaje de Success
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}  # Return success
    
@update_products_blueprint.route('/get-increment-list')
def price_profit_correction():

    """
    Los precios de la tienda estan con un margen del 13% pero se quieren subir todos
    al 15%, hay algunas excepciones como que los productos pequeños o accesorios van
    van a incrementar al 20%, tambien se tiene que tener en cuenta el valor del UVT
    para portatiles, celulares y tablets (50 UVT y 22 UVT).
    
    La nueva formula de ganancia es: precio / (1-13)
    13 es el porcentaje de ganancia
    """

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

@update_products_blueprint.route('/update-with-increment-list')
def update_with_increment_list():

    # Se guarda el registro dentro de "logs.json"
    with open(f'{project_folder}/data/product_prices.json') as f:

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
@update_products_blueprint.route("/round-up-prices")
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