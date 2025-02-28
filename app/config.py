from dotenv import load_dotenv
import os

load_dotenv()
SQLALCHEMY_DB_INFO = os.getenv("SQLALCHEMY_DB_INFO")
SALT_INFO = os.getenv("SALT_INFO")

class Config:


    # Databasinställningar
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+mysqlconnector://root:password@localhost:3310/Bank')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Security
    SECRET_KEY = os.getenv('SECRET_KEY', '{SECRET_KEY}')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', '{SALT_INFO}')
    SECURITY_LOGIN_USER_TEMPLATE = "security/login_user.html"
    SECURITY_UNAUTHORIZED_VIEW = "/unauthorized"
    SECURITY_FLASH_MESSAGES = True  



class ConfigDebug(Config):
    # Debug-konfiguration (för utveckling)
    DEBUG = True
    SQLALCHEMY_ECHO = False 

class ConfigProduction(Config):
    # Produktionskonfiguration (för live)
    DEBUG = False
    SQLALCHEMY_ECHO = False
