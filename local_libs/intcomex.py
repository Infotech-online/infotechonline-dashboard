import requests
import json
import hashlib
import datetime
import traceback

from dotenv import load_dotenv
import os

# Variables de entorno
project_folder = os.path.abspath(os.getcwd())
load_dotenv(os.path.join(project_folder, '.env'))

class intcomexConnection():

    def __init__(self):

        # Archivos utilizados para almacenar datos
        self.intcomex_products_file = f"{project_folder}/data/intcomex_products.json"
        self.logs_file = f"{project_folder}/data/logs.json"
        self.tokens_file = f"{project_folder}/data/tokens.json"

        # Modo de funcionamiento la API
        self.mode = "Prod" # Variable que define el modo de la API

        # Credentials

        if self.mode == "Prod":
            # Credenciales de la API (MODO PRODUCCIÓN)
            self.url = os.getenv("INTCOMEX_PROD_URL")
            self.api_key = os.getenv("INTCOMEX_PROD_API_KEY")
            self.access_key = os.getenv("INTCOMEX_PROD_ACCESS_KEY")

        elif self.mode == "Test":
            # Credenciales de la API (MODO TEST)
            self.url = os.getenv("INTCOMEX_TEST_URL")
            self.api_key = os.getenv("INTCOMEX_TEST_API_KEY")
            self.access_key = os.getenv("INTCOMEX_TEST_ACCESS_KEY")

    def generate_signature(self):
        
        # Se obtiene la fecha y hora actual
        utc_datetime = datetime.datetime.utcnow()
        utc_datetime.strftime("%Y-%m-%dT %H:%M:%SZ")

        # Se hace encode de la signature en sha256
        signature = f"{self.api_key},{self.access_key},{utc_datetime}"
        signature = signature.encode('utf-8')
        signature = hashlib.sha256(signature)
        signature = signature.hexdigest()

        return utc_datetime, signature
    
    def get_sku_list(self):

        with open(self.intcomex_products_file) as f:
            products_data = json.load(f)

        sku_list = []

        # Se obtienen todas las SKU's almacenadas en el archivo "intcomex_products.json"
        for category in products_data:  # Por cada categoría dentro de "intcomex_products.json"
            for sku in products_data[category]:  # Por cada SKU dentro de la categoría
                # Se concatena los datos del producto dentro de la variable "sku_list"
                sku_list.append(products_data[category][sku]["intcomexSku"])

        return sku_list
    
    def get_catalog(self):

        # Se genera una nueva signature para ejecutar la petición
        signature = self.generate_signature()
        # URL de petición: /getcatalog
        get_catalog_url = f'{self.url}getcatalog/?apiKey={self.api_key}&utcTimeStamp={signature[0]}&signature={signature[1]}&locale=es'

        try:
            # Se realiza y retorna el request
            return requests.get(get_catalog_url).json()

        except Exception as e:

            traceback.print_exc()
            # Obtener la información del error
            exc_traceback = traceback.format_exc()
            return exc_traceback

    def get_single_product(self, sku):

        # Se genera una nueva signature para ejecutar la petición
        signature = self.generate_signature()
        # URL de petición: /getproduct
        single_product_url = f'{self.url}getproduct/?apiKey={self.api_key}&utcTimeStamp={signature[0]}&signature={signature[1]}&sku={sku}&locale=es'
        
        try:
            # Se realiza la request para obtener un solo producto como resultado
            single_product_url = requests.get(single_product_url).json()
            return single_product_url
        
        except Exception as e:

            traceback.print_exc()
            # Obtener la información del error
            exc_traceback = traceback.format_exc()
            return exc_traceback

    def get_intcomex_prices_list(self, sku_list):
        
        # Se genera una nueva signature para ejecutar la petición
        signature = self.generate_signature()
        # URL de petición: /getpriceslist
        get_prices_url = f'{self.url}getpricelist/?apiKey={self.api_key}&utcTimeStamp={signature[0]}&signature={signature[1]}&locale=es'

        try:
            # Intcomex "getpricelist" request
            intcomex_prices = requests.get(get_prices_url).json()

            # Obtener solo los productos con el mismo SKU
            products = {product["Sku"]: product["Price"]["UnitPrice"] for product in intcomex_prices if product["Sku"] in sku_list}

            return products

        except Exception as e:

            traceback.print_exc()
            # Obtener la información del error
            exc_traceback = traceback.format_exc()
            return exc_traceback

    def get_intcomex_stock_list(self, sku_list):

        # Se genera una nueva signature para ejecutar la petición
        signature = self.generate_signature()
        # URL de petición: /getinvetory
        get_stock_url = f'{self.url}getinventory/?apiKey={self.api_key}&utcTimeStamp={signature[0]}&signature={signature[1]}&locale=es'

        try:
            # Se realiza el request de la petición
            intcomex_stock = requests.get(get_stock_url).json()

            print(intcomex_stock)

            # Obtener solo los productos con el mismo SKU
            products = {product["Sku"]: product["InStock"] for product in intcomex_stock if product["Sku"] in sku_list}

            return products

        except Exception as e:

            traceback.print_exc()
            # Obtener la información del error
            exc_traceback = traceback.format_exc()
            return exc_traceback

    def get_current_products(self):

        try:
            # Se obtiene la lista de SKU's
            sku_list = self.get_sku_list()
            # Se obtiene la lista de precios de Intcomex con la lista de SKU's
            price_list = self.get_intcomex_prices_list(sku_list)
            # Se obtiene la lista de stock de Intcomex con la lista de SKU's
            stock_list = self.get_intcomex_stock_list(sku_list)

            return sku_list, price_list, stock_list
        
        except Exception as e:

            traceback.print_exc()
            # Obtener la información del error
            exc_traceback = traceback.format_exc()
            return exc_traceback
        