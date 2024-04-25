from woocommerce import API
from dotenv import load_dotenv
import os

# Variables de entorno
project_folder = os.path.abspath(os.getcwd()) # Desarrollo
# project_folder = os.path.expanduser('~/infotechonline-dashboard') # Producción
load_dotenv(os.path.join(project_folder, '.env'))

class wooConnection():

    def __init__(self):

        # Credenciales de la API de Woocommerce
        self.wc = API(
            url = os.getenv("URL"),
            consumer_key = os.getenv('CONSUMER_KEY'),
            consumer_secret = os.getenv('CONSUMER_SECRET'),
            version = "wc/v3"
        )

    # Obtener un producto con el SKU de la tienda en formato JSON
    def get_product_by_sku(self, sku):

        try:
            # Se realiza una consulta a la API de woocommerce con el SKU del producto
            return self.wc.get("products", params={"sku": sku}).json()[0]
        except:
            # Si la consulta no se puede realizar se lanza el siguiente error:
            return "Error Woocommerce Api"

    # Obtener todos los productos de la tienda en formato JSON
    def get_all_prods(self, curr_page=1):

        # Se realiza la consulta de woocommerce para obtener todos los productos en un rango de 100
        # La API de woocommerce solo deja obtener 100 productos por consulta
        products = self.wc.get("products", params={'per_page': 100, 'page': curr_page}).json()
        current_page = products

        """ 
        Si la cantidad dep roductos es mayor o igual a 100 significa que hay mas productos
        Entonces se pasaria a realizar otra consulta hasta que ya no queden mas productos.
        """
        while len(current_page) >= 100:
            curr_page += 1
            # Se realiza la consulta nuevamente pero aumentando la paginación para avanzar a la otra pagina de productos
            current_page = self.wc.get("products", params={'per_page': 100, 'page': curr_page}).json()
            # Se concatena la lista de productos anterior con la nueva lista de productos
            products = products + current_page

        # Se retorna un JSON con todos los productos de la tienda concatenados
        return products
    
    # Obtener todas las imagenes de los productos de la tienda en formato JSON
    def get_all_imgs(self):

        """
        Esta funcion es utilizada para almacenar todas las imagenes dentro de "products_imgs.json"
        hasta el momento se debe actualizar manualmente este archivo.

        ( Las imagenes son cargadas dentro del dashboard con el enlace que se obtiene de la consulta )
        """
        
        # Se obtienen todos los productos de woocommerce
        all_products = self.get_all_prods()
        img_list = {}

        # Por cada producto dentro de "all_products" se obtiene la imagen y se almacena dentro de "img_list"
        for pos, product in enumerate(all_products):
            if len(product["images"]) > 0:
                img_list[product["id"]] = product["images"][0]["src"]

        # Se retorna un JSON con todas las imagenes
        return img_list

    # Realizar una consulta personalizada
    def mconsult(self):
        # Manual Consult
        return self.wc
        