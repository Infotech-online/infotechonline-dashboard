from flask import Flask, Blueprint, request, render_template, session, url_for, redirect, send_file
from dotenv import dotenv_values
import time
from datetime import datetime
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
get_data_bp = Blueprint('get_data', __name__)

# Ruta principal
@get_data_bp.route('/')
def dashboard():

    # Se retorna el template del dashboard
    return render_template("dashboard.html")

# Obtener datos locales mediante POST
@get_data_bp.route('/local-data', methods=["POST"])
def infotech_data():
    
    """
    Obtiene los datos locales almacenados dentro de los archivos para 
    retornarlos en una petición post dentro de una misma variable nombrada
    "data" un diccionario de variables.
    """

    # Si el metodo de petición es POST
    if request.method == "POST":

        # Obtener el parametro de pagina de producto
        page = request.form["page"]

        # Se obtienen todos los productos de Woocommerce que esten en la pagina especifica
        products = woo.get_all_prods(int(page))

        # Obtener las imagenes de los productos almacenadas en "products_imgs.json"
        with open('data/products_imgs.json') as f:
            imgs = json.load(f)

        # Obtener datos de registros de actualizaciónes
        logs = logRecorder()
        logs_data = logs.logs_data

        # Obtener los registros por fechas
        logs_data_today, today_log_qty, last_log_date = logs.get_logs_by_date()

        # Obtener la cantidad de registros en total
        logs_qty = logs.get_log_quantity()

        # Se guardan los datos dentro de una unica variable para pasarla al DOM
        data = {}
        data["products"] = products
        data["logs"] = logs_data_today
        data["logs_qty"] = logs_qty

        # Si la cantidad de registros es mayor a 0
        if len(logs_data["logs"]) > 0:
            # Se almacena la fecha de la ultima actualización realizada
            data["last_log_date"] = last_log_date
        else:
            # Si no hay registros la fecha sera "(Null)"
            data["last_log_date"] = "(Null)"

        # Se almacena la cantidad de registros del día
        data["today_log_qty"] = today_log_qty
        # Se devuelven las imagenes
        data["imgs"] = imgs

        # Se retornan todos los datos obtenidos
        return data
    
    else:
        # Si la petición es de un tipo deferente a POST
        return "No deberias estar viendo esta pagina."