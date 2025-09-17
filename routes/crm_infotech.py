from flask import Flask, Blueprint, request, jsonify, current_app, send_file
from local_libs.wallet_mysql import mysqlConnection_wallet
from functools import wraps
import datetime
import requests
import pandas as pd
from sodapy import Socrata

# Librerías para manejo de documentos
from docxtpl import DocxTemplate, RichText
from io import BytesIO

# Blueprint
crm_blueprint = Blueprint('crm_blueprint', __name__)

# RUTAS DE LA API -------------------------------------------------------------------------------------------

@crm_blueprint.route('/crm_api/cotizacion', methods=['POST'])
def crm_infotech_word_template():

    data = request.json

    # Información primeria de la oportunidad
    fecha_oportunidad = data.get('fecha_oportunidad', None)
    cuenta_oportunidad = data.get('cuenta_oportunidad', None)
    contacto_oportunidad = data.get('contacto_oportunidad', None)
    cargo_contacto = data.get('cargo_contacto', None)
    numero_oportunidad = data.get('numero_oportunidad', None)

    # Información de los productos en la oportunidad
    productos_oportunidad = data.get('productos_oportunidad', None)

    # Información del usuario que crea la oportunidad
    usuario_propietario = data.get('usuario_propietario', None)
    cargo_usuario = data.get('cargo_usuario', None)
    telefono_usuario = data.get('telefono_usuario', None)

    # Contexto del documento
    context = {
        'fecha_oportunidad': fecha_oportunidad,
        'cuenta_oportunidad': cuenta_oportunidad,
        'contacto_oportunidad': contacto_oportunidad,
        'cargo_contacto': cargo_contacto,
        'numero_oportunidad': numero_oportunidad,

        'products': productos_oportunidad,

        'nombre_usuario': usuario_propietario,
        'cargo_usuario': cargo_usuario,
        'celular_usuario': telefono_usuario
    }

    try:
        # Ruta del proyecto
        with current_app.app_context():
            project_folder = current_app.config["PROJECT_FOLDER"]
            word_template = DocxTemplate(f"{project_folder}/data/templates/Modelo_cotizacion.docx")
            word_template.render(context)

            buffer = BytesIO()
            word_template.save(buffer)
            buffer.seek(0)

            # Enviar el archivo directamente como descarga
            return send_file(
                buffer,
                as_attachment=True,
                download_name="Cotizacion_generada.docx",
                mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        # return jsonify({'success': "Se ha generado la cotización con éxito."}), 200

    except Exception as e:

        return jsonify({'error': f"Error al generar la cotización: {str(e)}"}), 500

"""
cdn_blueprint = Blueprint('cdn_blueprint', __name__)

@cdn_blueprint.route("/cdn/<path:filename>")
def cdn_route(filename):
    ruta_cdn = os.path.join(os.path.dirname(__file__), '..', 'cdn/')
    return send_from_directory(ruta_cdn, filename)"""

@crm_blueprint.route('/crm-infotech')
def crm_infotech_gov():

    # Unauthenticated client only works with public data sets. Note 'None'
    # in place of application token, and no username or password:
    # client = Socrata("www.datos.gov.co", None)

    # Example authenticated client (needed for non-public datasets):
    client = Socrata("www.datos.gov.co",
    				"ZfkMLeKWpD2dq3WscpMmmGmOP",
    				username="hf2264185@gmail.com",
    				password="2GwR$4p$Fy87D-5")

    # First 2000 results, returned as JSON from API / converted to Python list of
    # dictionaries by sodapy.
    results = client.get("rpmr-utcd", limit=500, estado_del_proceso="Convocado")

    # Convert to pandas DataFrame
    # results_df = pd.DataFrame.from_records(results)

    return jsonify(results)