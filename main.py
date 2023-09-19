from flask import Flask, request, render_template, session, url_for, redirect, send_file
from dotenv import dotenv_values
from woocommerce import API
import random
import os
import time
import datetime
import json
import smtplib

app = Flask(__name__, template_folder='templates', static_folder='static')

# Env Vars
env = dotenv_values(".env")

# Session vars
app.secret_key = "super secret key"

# WooCommerce API Credentials

wc = API(
    url = env["URL"],
    consumer_key = env['CONSUMER_KEY'],
    consumer_secret = env['CONSUMER_SECRET'],
    version = "wc/v3"
)

# Products SKU
# Productos a los cuales se les va a cambiar el precio

with open('products.json') as f:
    products_data = json.load(f)


@app.route('/')
def dashboard():

    """r = wc.get("products", params={'per_page': 100})
    r.status_code"""
    
    # return render_template("dashboard.html", status_code=r.json())
    
    sku = "101001"
    r = wc.get("products", params={'sku': sku})
    return r.json()


if __name__ == '__main__':

    app.run(debug=True, host="0.0.0.0")
