import requests
import json
from dotenv import dotenv_values
import time

# Env Vars
env = dotenv_values(".env")

class intcomexConnection():

    def __init__(self):

        # Files
        self.intcomex_products_file = "intcomex_products.json"
        self.logs_file = "logs.json"
        self.tokens_file = "tokens.json"

    def generate_signature(self):

        pass