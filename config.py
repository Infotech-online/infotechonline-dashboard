from dotenv import load_dotenv
import os

# Variables de entorno
project_folder = os.path.abspath(os.getcwd()) # Desarrollo
# project_folder = os.path.expanduser('~/infotechonline-dashboard') # Producción
load_dotenv(os.path.join(project_folder, '.env'))

class Config:
    DEBUG = False
    TESTING = False
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME") # Tu dirección de correo electrónico
    MAIL_PASSWORD =  os.getenv("MAIL_PASSWORD") # Tu contraseña de aplicación generada para acceso desde apps externas

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    MAIL_USE_TLS = True
    MAIL_PORT = 587

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}