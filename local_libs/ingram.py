import requests
import json
from dotenv import dotenv_values
import time

# Env Vars
env = dotenv_values(".env")

class ingramConnection():

    """
    Clase para gestionar la conexión con la API de Ingram.
    """

    def __init__(self):

        # Archivos
        self.ingram_products_file = 'ingram_products.json'
        self.logs_file = 'logs.json'
        self.tokens_file = 'tokens.json'

        # Credenciales
        self.client_id = env["INGRAM_CLIENT_ID"]
        self.client_secret = env["INGRAM_CLIENT_SECRET"]
        self.customer_number = env["INGRAM_CUSTOMER_NUMBER"]

        # URL de las APIs
        self.token_url = f'https://api.ingrammicro.com:443/oauth/oauth20/token?grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}'
        self.api_url = f'https://api.ingrammicro.com:443/resellers/v5'

    # Generar un token para realizar las peticiones a la API
    def generate_token(self):
        
        """
        El token de Ingram se genera y tiene un periodo de validez, este periodo
        define durante cuanto tiempo se puede usar, si el token expira se procede a
        obtener uno nuevo y se almacena dentro de "tokens.json"
        """

        # Se abre el archivo de tokens
        with open(self.tokens_file) as f:
            tokens = json.load(f)

        # Si la fecha de expiración del token es menor al tiempo actual
        # Significa que el token ya expiro
        if tokens["ingram"]["expires_in"][0] < time.time():

            
            # Se forma la consulta para generar un nuevo Tokens
            response = requests.get(self.token_url, headers={"Content-Type": "application/x-www-form-urlencoded"})
            response = response.json()
            # Se suma el tiempo actual con la duración del token que se recibio como respuesta de la petición
            expires = time.time() + int(response["expires_in"])
            
            # Estructura para almacenar la información del nuevo token en el archivo "tokens.json"
            new_token_data = {
                "access_token": response["access_token"],
                "expires_in": [expires, time.ctime(expires)]
            }

            # Se abre el archivo "tokens.json"
            with open(self.tokens_file) as f:
                tokens = json.load(f)
                tokens["ingram"] = new_token_data
                new_data = json.dumps(tokens, indent=4)

            # Se escribe la nueva información dentro del archivo "tokens.json"
            with open(self.tokens_file, 'w') as file:
                file.write(new_data)

            # Se retorna el nuevo token de acceso
            return response["access_token"]

        else:

            # Si el token no ha expirado, se envia el mismo token guardado dentro del archivo "tokens.json"
            return tokens["ingram"]["access_token"]

    # Obtener todos los productos de ingram
    def get_products(self):

        """
        Obtiene todos los productos de Ingram mediante una consulta a la API.
        Retorna la respuesta de la API y una lista de SKUs utilizados en la consulta.
        """
        
        # URL de la petición: /catalog/priceandavailability
        catalog_url = self.api_url + f"/catalog/priceandavailability?customerNumber={self.customer_number}&isoCountryCode=CO"
        # Se pasa el token de acceso mediante "Bearer"
        token = f"Bearer {self.generate_token()}"

        # Headers de la consulta
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": token,
        }

        # Listado de Items
        items = []
        # Listado de SKUs
        sku_list = []

        # Se abre el archivo "ingram_products.json"
        with open('ingram_products.json') as f:
            products_data = json.load(f)

        # Por cada categoría dentro del archivo "ingram_products.json"
        for category in products_data:
            # Por cada SKU dentro de cada categoría
            for sku in products_data[category]:  # Sku and Prices

                # Estructura del producto para la consulta
                new_item = {
                    "ingrampartnumber": products_data[category][sku]["ingramSku"],
                    "quantity": 1
                }
                # Se almacena el producto dentro de "items"
                items.append(new_item)
                # Se agrega el SKU interno del producto dentro de "sku_list"
                sku_list.append(sku)
            
        # Datos de la consulta
        """
        Se pasa la variable "items" para realizar la consulta con todos
        los productos que esten almacenados dentro del archivo
        "ingram_products.json"

        """
        data = {
            "servicerequest": {
                "requestpreamble": {
                    "customernumber": self.customer_number,
                    "isocountrycode": "CO"
                },
                "priceandstockrequest": {
                    "showwarehouseavailability": "True",
                    "extravailabilityflag": "Y",
                    "item": items,
                    "includeallsystems": False
                }
            }
        }

        # Se genera un request a la URL del catalogo de Ingram con los datos y headers
        response = requests.post(catalog_url, headers=headers, json=data)
        response = response.json()["serviceresponse"]["priceandstockresponse"]["details"]

        # Se retorna la respuesta de la petición y la lista de SKUs que se utilizaron en el request
        return response, sku_list

    # Retornar unicamente el listado de precios de Ingram
    def return_all_prices(self):

        """
        Retorna un diccionario que contiene los precios de los productos de Ingram.
        """
    
        # Se obtienen los productos de Ingram
        products = self.get_products()[0]

        # Se inicializa una nueva variable que almacenara el listado de precios
        new_product_list = {}

        # Por cada producto dentro del listado de productos
        for product in products:

            """
            Se obtiene unicamente el precio del producto y se almacena con el
            numero de parte que usa Ingram, para luego ser llamado facilmente.
            """
            new_product_list[product["ingrampartnumber"]] = product["customerprice"]

        # Se retorna el listado de precios
        return new_product_list

    # Retornar unicamente el stock de un producto en especifico de Ingram
    def return_stock(self, sku) -> int:

        """
        Retorna el stock de un producto específico de Ingram dado su SKU.
        """
        
        # Se obtienen los productos de Ingram
        products = self.get_products()[0]
        total_stock = 0
        
        # Por cada producto dentro del listado de productos
        for product in products:
            # Si el numero de parte es igual al SKU ingresado
            if product["ingrampartnumber"] == sku:
                # Por cada proveedor del producto
                for provider in product["warehousedetails"]:
                    # Se suma el stock del producto
                    total_stock += provider["availablequantity"]

        # Se retorna el stock del producto
        return total_stock
    
    # Retornar unicamente el listado de stock de los productos de Ingram
    def return_all_stock(self):

        """
        Retorna un diccionario que contiene el stock de todos los productos de Ingram.
        """

        # Se obtienen los productos de Ingram
        products = self.get_products()[0]

        # Se inicializa una nueva variable que almacenara el listado de stock
        all_stock = {}

        # Por cada producto dentro del listado de productos
        for product in products:

            # Stock incial
            stock = 0
            # Por cada proveedor dentro del producto
            for provider in product["warehousedetails"]:
                # Se suma el stock del prodcuto
                stock += provider["availablequantity"]

            # Se agrega el stock del producto con el numero de parte
            all_stock[product["ingrampartnumber"]] = stock

        # Se retorna un listado JSON con todos los valores de stock de los productos internos.
        return all_stock

