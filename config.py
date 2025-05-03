import os
from pathlib import Path
import secrets
from dotenv import load_dotenv
import logging

# Get the absolute path to the flask-app directory
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Security settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    SESSION_COOKIE_SECURE = True  # Required for production HTTPS
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 3600
    PREFERRED_URL_SCHEME = 'https'  # Required for production
    
    # Database settings
    url = os.environ.get("DATABASE_URL", 'sqlite:///' + os.path.join(basedir, 'app.db'))
    url = url.replace("postgres://", "postgresql://")
    if "sslmode" not in url and "postgresql://" in url:
        url += "?sslmode=require"
    SQLALCHEMY_DATABASE_URI = url
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']

    @staticmethod
    def init_app(app):
        # Create the app directory if it doesn't exist
        app_dir = Path(app.instance_path).parent
        app_dir.mkdir(exist_ok=True)
        
        # Ensure the database directory exists
        db_dir = app_dir
        db_dir.mkdir(exist_ok=True)
        
        # Log the final database URI
        logging.info(f"Initializing app with database URI: {Config.SQLALCHEMY_DATABASE_URI}")

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SESSION_COOKIE_SECURE = False
    PREFERRED_URL_SCHEME = 'http'
    
class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
} 