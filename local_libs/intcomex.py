import requests
import json
from dotenv import dotenv_values
import time
import hashlib
import datetime
import threading
import traceback

# Env Vars
env = dotenv_values(".env")

class intcomexConnection():

    def __init__(self):

        # Files
        self.intcomex_products_file = "intcomex_products.json"
        self.logs_file = "logs.json"
        self.tokens_file = "tokens.json"

        # Mode
        self.mode = "Prod" # This var could change

        # Credentials

        if self.mode == "Prod":
            # PROD CREDENTIALS
            self.url = env["INTCOMEX_PROD_URL"]
            self.api_key = env["INTCOMEX_PROD_API_KEY"]
            self.access_key = env["INTCOMEX_PROD_ACCESS_KEY"]

        elif self.mode == "Test":
            # TEST CREDENTIALS
            self.url = env["INTCOMEX_TEST_URL"]
            self.api_key = env["INTCOMEX_TEST_API_KEY"]
            self.access_key = env["INTCOMEX_TEST_ACCESS_KEY"]

    def generate_signature(self):
        
        # Generate the signature required to make the Intcomex API consult
        utc_datetime = datetime.datetime.utcnow()
        utc_datetime.strftime("%Y-%m-%dT %H:%M:%SZ")

        # The signature is encode in Sha256
        signature = f"{self.api_key},{self.access_key},{utc_datetime}"
        signature = signature.encode('utf-8')
        signature = hashlib.sha256(signature)
        signature = signature.hexdigest()

        return utc_datetime, signature
    
    def get_sku_list(self):

        with open('intcomex_products.json') as f:
                products_data = json.load(f)

        skus = []

        # Get all SKU for each category in the "intcomex_products.json" file
        for category in products_data:  # Categories
            for sku in products_data[category]:  # Sku and Prices
                skus.append(products_data[category][sku]["intcomexSku"])

        return skus
    
    def get_catalog(self):

        signature = self.generate_signature()
        get_catalog_url = f'{self.url}getcatalog/?apiKey={self.api_key}&utcTimeStamp={signature[0]}&signature={signature[1]}&locale=es'

        try:
            return requests.get(get_catalog_url).json()

        except Exception as e:

            traceback.print_exc()
            # Obtener la información de la traza
            exc_traceback = traceback.format_exc()
            return exc_traceback

    def get_single_product(self, sku):

        signature = self.generate_signature()
        single_product_url = f'{self.url}getproduct/?apiKey={self.api_key}&utcTimeStamp={signature[0]}&signature={signature[1]}&sku={sku}&locale=es'
        
        try:
            single_product_url = requests.get(single_product_url).json()
            return single_product_url
        
        except Exception as e:

            traceback.print_exc()
            # Obtener la información de la traza
            exc_traceback = traceback.format_exc()
            return exc_traceback

    def get_intcomex_prices_list(self, sku_list):

        signature = self.generate_signature()
        get_prices_url = f'{self.url}getpricelist/?apiKey={self.api_key}&utcTimeStamp={signature[0]}&signature={signature[1]}&locale=es'

        try:
            # Intcomex "getpricelist" request
            intcomex_prices = requests.get(get_prices_url).json()

            # Only get products with the same SKU
            products = {product["Sku"]: product["Price"]["UnitPrice"] for product in intcomex_prices if product["Sku"] in sku_list}

            return products

        except Exception as e:

            traceback.print_exc()
            # Obtener la información de la traza
            exc_traceback = traceback.format_exc()
            return exc_traceback

    def get_intcomex_stock_list(self, sku_list):

        signature = self.generate_signature()
        get_stock_url = f'{self.url}getinventory/?apiKey={self.api_key}&utcTimeStamp={signature[0]}&signature={signature[1]}&locale=es'

        try:
            # Intcomex "getpricelist" request
            intcomex_stock = requests.get(get_stock_url).json()

            # Only get products with the same SKU
            products = {product["Sku"]: product["InStock"] for product in intcomex_stock if product["Sku"] in sku_list}

            return products

        except Exception as e:

            traceback.print_exc()
            # Obtener la información de la traza
            exc_traceback = traceback.format_exc()
            return exc_traceback

    def get_current_products(self):

        try:
            sku_list = self.get_sku_list()
            price_list = self.get_intcomex_prices_list(sku_list)
            stock_list = self.get_intcomex_stock_list(sku_list)

            return sku_list, price_list, stock_list
        
        except Exception as e:

            traceback.print_exc()
            # Obtener la información de la traza
            exc_traceback = traceback.format_exc()
            return exc_traceback
        