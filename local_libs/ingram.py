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

        # Urls
        self.token_url = f'https://api.ingrammicro.com:443/oauth/oauth20/token?grant_type=client_credentials&client_id={env["INGRAM_CLIENT_ID"]}&client_secret={env["INGRAM_CLIENT_SECRET"]}'
        self.api_url = f'https://api.ingrammicro.com:443/resellers/v5'

        self.get_products()

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

        catalog_url = self.api_url + "/catalog/priceandavailability?customerNumber=216793&isoCountryCode=CO&partNumber=5734408"
        token = f"Bearer {self.generate_token()}"

        # Headers of the cosult
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": token,
        }

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
                    "item": [
                        {
                            "ingrampartnumber": "5734408",
                            "quantity": 1
                        }
                    ],
                    "includeallsystems": False
                }
            }
        }

        response = requests.post(catalog_url, headers=headers, json=data)

        return response.json()

ingramConnection()