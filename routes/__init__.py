from flask import Blueprint

def create_routes_blueprint(mail, config):

    # Se importan las Blueprints
    from .get_data import get_data_blueprint
    from .update_products import update_products_blueprint
    from .debugging import debugging_blueprint
    from .email import email_blueprint
    from .cdn import cdn_blueprint
    from .price_increase import price_increase_blueprint

    from .wallet import wallet_blueprint
    # Crea un Blueprint para las rutas
    routes_blueprint = Blueprint('routes', __name__)

    print(config.PROJECT_FOLDER)

    # Registra los Blueprints en este módulo
    routes_blueprint.register_blueprint(get_data_blueprint, config=config)
    routes_blueprint.register_blueprint(update_products_blueprint, config=config)
    routes_blueprint.register_blueprint(debugging_blueprint, config=config)
    routes_blueprint.register_blueprint(email_blueprint, mail=mail, config=config)
    routes_blueprint.register_blueprint(cdn_blueprint, config=config)
    routes_blueprint.register_blueprint(price_increase_blueprint, config=config)
    routes_blueprint.register_blueprint(wallet_blueprint)
    
    return routes_blueprint