from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize the Config class
    config_class.init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    with app.app_context():
        # Import blueprints
        from app.routes.auth import bp as auth_bp
        from app.routes.assessment import bp as assessment_bp
        from app.routes.main import bp as main_bp
        from app.routes.health import bp as health_bp
        
        # Register blueprints
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(assessment_bp, url_prefix='/assessment')
        app.register_blueprint(main_bp)  # No url_prefix for main blueprint
        app.register_blueprint(health_bp)  # No url_prefix for health checks
        
        # Create database tables
        db.create_all()
    
    return app 