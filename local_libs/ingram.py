import requests
import json
from dotenv import dotenv_values
import time

# Env Vars
env = dotenv_values(".env")

class ingramConnection():

    def __init__(self):

        # Files
        self.ingram_products_file = 'ingram_products.json'
        self.logs_file = 'logs.json'
        self.tokens_file = 'tokens.json'

        # Credentials
        self.client_id = env["INGRAM_CLIENT_ID"]
        self.client_secret = env["INGRAM_CLIENT_SECRET"]
        self.customer_number = env["INGRAM_CUSTOMER_NUMBER"]

        # Urls
        self.token_url = f'https://api.ingrammicro.com:443/oauth/oauth20/token?grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}'
        self.api_url = f'https://api.ingrammicro.com:443/resellers/v5'

    def generate_token(self):

        with open(self.tokens_file) as f:
            tokens = json.load(f)

        if tokens["ingram"]["expires_in"][0] < time.time():

            # Invalid Token (expired)

            response = requests.get(self.token_url, headers={"Content-Type": "application/x-www-form-urlencoded"})
            response = response.json()
            expires = time.time() + int(response["expires_in"])
            
            new_token_data = {
                "access_token": response["access_token"],
                "expires_in": [expires, time.ctime(expires)]
            }

            with open(self.tokens_file) as f:
                tokens = json.load(f)
                tokens["ingram"] = new_token_data
                new_data = json.dumps(tokens, indent=4)

            with open('tokens.json', 'w') as file:
                file.write(new_data)

            return response["access_token"]

        else:

            # Valid Token      
            return tokens["ingram"]["access_token"]

    def get_products(self):

        catalog_url = self.api_url + f"/catalog/priceandavailability?customerNumber={self.customer_number}&isoCountryCode=CO"
        token = f"Bearer {self.generate_token()}"

        # Headers of the cosult
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": token,
        }

        items = []
        sku_list = []

        with open('ingram_products.json') as f:
            products_data = json.load(f)

        for category in products_data:  # Categories
            for sku in products_data[category]:  # Sku and Prices
                new_item = {
                    "ingrampartnumber": products_data[category][sku]["ingramSku"],
                    "quantity": 1
                }
                items.append(new_item)
                sku_list.append(sku)
            
        # Product data
        data = {
            "servicerequest": {
                "requestpreamble": {
                    "customernumber": "216793",
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

        response = requests.post(catalog_url, headers=headers, json=data)
        response = response.json()["serviceresponse"]["priceandstockresponse"]["details"]
    
        return response, sku_list

    def return_prices(self):

        products = self.get_products()[0]
        sku_list = self.get_products()[1]

        price_data = {}

        for pos, product in enumerate(products):
            price_data[sku_list[pos]] = product["customerprice"]

        return price_data

    def return_stock(self, sku):

        products = self.get_products()[0]
        total_stock = 0
        
        for product in products:
            if product["ingrampartnumber"] == sku:
                for provider in product["warehousedetails"]:
                    total_stock += provider["availablequantity"]

        return total_stock
    
    def return_all_stock(self):

        all_stock = {}

        for product in self.get_products()[0]:

            stock = 0
            for provider in product["warehousedetails"]:
                stock += provider["availablequantity"]

            all_stock[product["ingrampartnumber"]] = stock

        return all_stock

