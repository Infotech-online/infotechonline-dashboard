from dotenv import dotenv_values

# Variables de entorno
env = dotenv_values(".env")

class Config:
    DEBUG = False
    TESTING = False
    MAIL_SERVER = env["MAIL_SERVER"]
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = env["MAIL_USERNAME"] # Tu dirección de correo electrónico
    MAIL_PASSWORD =  env["MAIL_PASSWORD"] # Tu contraseña de aplicación generada para acceso desde apps externas

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