from flask import Flask
from flask_mail import Mail
from flask_cors import CORS
from routes import create_routes_blueprint
from config import config

def create_app(env):

    # Se inicializa la App de Flask
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Session vars
    app.secret_key = "super secret key"

    # CORS
    CORS(app, resources={r"/*": {"origins": "https://infotechonline.co"}})

    # Config Data
    app.config.from_object(config[env])
    
    # Configuracion del SMTP
    mail = Mail(app)

    # Registra el Blueprint de rutas en la aplicación
    app.register_blueprint(create_routes_blueprint(mail, config[env]))

    return app

enviroment = 'development' # Entorno actual
app = create_app(enviroment)

# Se inicializa el programa
if __name__ == '__main__':

    app.run(debug=True, host="0.0.0.0", port=1010)