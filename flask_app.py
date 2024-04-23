from flask import Flask

# Se inicializa la App de Flask
app = Flask(__name__, template_folder='templates', static_folder='static')

# Se importan las Blueprints
from routes.get_data import get_data_bp
from routes.update_products import update_products_bp
from routes.debugging import debugging_bp

# Se cargan los Blueprints
app.register_blueprint(get_data_bp)
app.register_blueprint(update_products_bp)
app.register_blueprint(debugging_bp)

# Se inicializa el programa
if __name__ == '__main__':

    app.run(debug=True, host="0.0.0.0", port=1010)