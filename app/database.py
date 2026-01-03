"""
Database module with db instance to avoid circular imports
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions without app - will be initialized later
db = SQLAlchemy()
login_manager = LoginManager()

def init_db(app):
    """
    Initialize database with app
    """
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    return db, login_manager