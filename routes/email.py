from flask import request, Blueprint, jsonify, current_app
import base64
import os
from flask_mail import Message
from local_libs.wallet_email import mysqlConnection_wallet_correo

correo = mysqlConnection_wallet_correo()

# Blueprint
email_blueprint = Blueprint('email_blueprint', __name__)

@email_blueprint.route('/save_pdf', methods=['POST'])
def guardar_pdf():

    if request.method == 'POST':

        # Se carga el contexto de la aplicación de Flask
        with current_app.app_context():

            # Código que utiliza current_app
            mail = current_app.extensions['mail']

        data = request.json  # Obtiene los datos del cuerpo de la solicitud en formato JSON

        # Trabaja con los datos recibidos
        pdf_file = data.get('pdf_file')
        pdf_name = data.get('pdf_name')
        quotation_number = data.get('pdf_number')
        email_recipent = data.get('email_recipent')

        # Get the encoded section from the data URI string
        _, base64_data = pdf_file.split(',')

        # Decode the Base64-encoded string to binary data
        pdf_bytes = base64.b64decode(base64_data)

        ruta_archivo = os.path.join(os.path.dirname(__file__), '..', 'documents/price_quotes/', pdf_name)

        # Save the binary data into a PDF file
        with open(ruta_archivo, 'wb') as file:
            file.write(pdf_bytes)

        try:
            
            # Crear un mensaje
            message = Message(subject=f'Infotechonline Cotización Numero {quotation_number}', sender=('Infotech', 'mercadeodigital@infotech.com.co'), recipients=[email_recipent])
            message.html = f"""
            <html>
            <head></head>
            <body>
                <h2>Cotización numero {quotation_number}</h2>
                <p>Si requieres mas información sobre las cotizaciones, realiza una respuesta a este correo.</p>
            </body>
            </html>
            """

            # Adjuntar un archivo (en este caso, archivo.pdf en la carpeta static)
            with email_blueprint.open_resource(ruta_archivo) as archivo_adjunto:
                message.attach(pdf_name, "application/pdf", archivo_adjunto.read())

            # Enviar el correo electrónico
            mail.send(message)

            response = {
                "status": "success",
                "message": "Operación realizada con éxito"
            }

            return jsonify(response), 200
        
        except Exception as e:
            return str(e)

@email_blueprint.route('/api/wallet/codigo_verificacion/<int:id>', methods=['POST'])
def send_code_verification(id):
    with current_app.app_context():
    # Código que utiliza current_app
        app = current_app.extensions['mail']
    
    resultado = correo.create_codigo_verificacion(id, app)
    # Retornar la respuesta
    return jsonify({'message': resultado})
