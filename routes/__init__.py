from flask import Blueprint

def create_routes_blueprint(mail):

    # Se importan las Blueprints
    from .get_data import get_data_blueprint
    from .update_products import update_products_blueprint
    from .debugging import debugging_blueprint
    from .email import email_blueprint
    from .cdn import cdn_blueprint

    # Crea un Blueprint para las rutas
    routes_blueprint = Blueprint('routes', __name__)    

    # Registra los Blueprints en este módulo
    routes_blueprint.register_blueprint(get_data_blueprint)
    routes_blueprint.register_blueprint(update_products_blueprint)
    routes_blueprint.register_blueprint(debugging_blueprint)
    routes_blueprint.register_blueprint(email_blueprint, mail=mail)
    routes_blueprint.register_blueprint(cdn_blueprint)
    
    return routes_blueprint