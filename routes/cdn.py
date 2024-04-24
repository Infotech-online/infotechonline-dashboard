from flask import Flask, Blueprint, send_from_directory
import os

# Blueprint
cdn_blueprint = Blueprint('cdn_blueprint', __name__)

@cdn_blueprint.route("/cdn/<path:filename>")
def cdn_route(filename):
    ruta_cdn = os.path.join(os.path.dirname(__file__), '..', 'cdn/')
    return send_from_directory(ruta_cdn, filename)