"""
Flask extensions initialization
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def init_extensions(app):
    """Initialize Flask extensions with app instance"""
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    
    # Set up login manager settings
    login_manager.refresh_view = 'login'
    login_manager.needs_refresh_message = 'Please log in again to access this page.'
    login_manager.needs_refresh_message_category = 'info'