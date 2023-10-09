import requests
import json
from dotenv import dotenv_values
import time
import hashlib
import datetime

# Env Vars
env = dotenv_values(".env")

class intcomexConnection():

    def __init__(self):

        # Files
        self.intcomex_products_file = "intcomex_products.json"
        self.logs_file = "logs.json"
        self.tokens_file = "tokens.json"

        # Urls
        self.url = env["INTCOMEX_URL"]

        # Credentials
        self.api_key = env["API_KEY"]
        self.access_key = env["ACCESS_KEY"]

    def generate_signature(self):

        utc_datetime = datetime.datetime.utcnow()
        utc_datetime.strftime("%Y-%m-%dT %H:%M:%SZ")

        signature = f"{self.api_key},{self.access_key},{utc_datetime}"
        signature = signature.encode('utf-8')
        signature = hashlib.sha256(signature)
        signature = signature.hexdigest()

        return signature
    
    def get_products(self):

        utc_datetime = datetime.datetime.utcnow()
        utc_datetime.strftime("%Y-%m-%dT %H:%M:%SZ")

        url = f'{self.url}getcatalog/?apiKey={self.api_key}&utcTimeStamp={utc_datetime}&signature={self.generate_signature()}&locale=es'
        
        try:
            url = requests.get(url).json()
            return url
        except:
            return "Error"

    def get_single_product(self, sku):

        utc_datetime = datetime.datetime.utcnow()
        utc_datetime.strftime("%Y-%m-%dT %H:%M:%SZ")

        url = f'{self.url}getproduct/?apiKey={self.api_key}&utcTimeStamp={utc_datetime}&signature={self.generate_signature()}&sku={sku}&locale=es'
        
        try:
            url = requests.get(url).json()
            return url
        except:
            return "Error"
