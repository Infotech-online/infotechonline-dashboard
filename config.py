from dotenv import load_dotenv
import os

"""
La variable de entorno ENVIRONMENT se cambia segun el entorno
"""

# Establece una variable de entorno
# os.environ['ENVIRONMENT'] = 'production'
os.environ['ENVIRONMENT'] = 'development'

# Lee la variable de entorno que indica el entorno actual
environment = os.getenv('ENVIRONMENT')  # Por defecto es 'development' si no está configurada

# Define el project_folder basado en el entorno
if environment == 'production':
    project_folder = os.path.expanduser('~/infotechonline-dashboard')
else:
    project_folder = os.path.abspath(os.getcwd())

load_dotenv(os.path.join(project_folder, '.env'))

class Config:
    DEBUG = False
    TESTING = False
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME") # Tu dirección de correo electrónico
    MAIL_PASSWORD =  os.getenv("MAIL_PASSWORD") # Tu contraseña de aplicación generada para acceso desde apps externas
    UVT = 47065 # Valor del UVT (Año 2024)

class DevelopmentConfig(Config):
    DEBUG = True
    PROJECT_FOLDER = os.path.abspath(os.getcwd())

class ProductionConfig(Config):
    DEBUG = False
    PROJECT_FOLDER = os.path.expanduser('~/infotechonline-dashboard')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}