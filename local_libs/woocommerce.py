from woocommerce import API
from dotenv import dotenv_values
import json

# Env Vars
env = dotenv_values(".env")

class wooConnection():

    def __init__(self):

        # WooCommerce API Credentials
        self.wc = API(
            url=env["URL"],
            consumer_key=env['CONSUMER_KEY'],
            consumer_secret=env['CONSUMER_SECRET'],
            version="wc/v3"
        )

    def get_product_by_sku(self, sku):

        try:
            return self.wc.get("products", params={"sku": sku}).json()[0]
        except:
            return "Error Woocommerce Api"

    def get_all_prods(self):

        curr_page = 1
        products = self.wc.get("products", params={'per_page': 100, 'page': curr_page}).json()
        current_page = products

        while len(current_page) >= 100:
            print("se extiende")
            curr_page += 1
            current_page = self.wc.get("products", params={'per_page': 100, 'page': curr_page}).json()
            products = products + current_page

        return products
        
    def get_all_imgs(self):

        all_products = self.get_all_prods()
        img_list = {}

        for pos, product in enumerate(all_products):
            if len(product["images"]) > 0:
                img_list[product["id"]] = product["images"][0]["src"]

        return img_list

    def mconsult(self):
        # Manual Consult
        return self.wc
        