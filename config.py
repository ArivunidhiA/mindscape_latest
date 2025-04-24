import os
from pathlib import Path
import secrets

# Get the absolute path to the flask-app directory
basedir = Path(__file__).resolve().parent

class Config:
    # Generate a secure random secret key
    SECRET_KEY = secrets.token_hex(32)
    
    # Use absolute path for database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(basedir / 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security settings
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Mail settings
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    ADMINS = ['your-email@example.com']

    @staticmethod
    def init_app(app):
        # Create the app directory if it doesn't exist
        app_dir = Path(app.instance_path).parent
        app_dir.mkdir(exist_ok=True)
        
        # Ensure the database directory exists
        db_dir = app_dir
        db_dir.mkdir(exist_ok=True) 