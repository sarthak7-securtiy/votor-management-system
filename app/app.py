from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from app.database import init_db

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'postgresql://user:password@localhost:5432/voter_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db, login_manager = init_db(app)

# Import models after db initialization to avoid circular imports
from app.models.user import User, load_user
from app.models.voter import Voter
from app.models.star_log import StarLog

# Register the user loader
login_manager.user_loader(load_user)

# Create tables
with app.app_context():
    db.create_all()
    
    # Create main user if not exists
    try:
        if not User.query.filter_by(role='main').first():
            from werkzeug.security import generate_password_hash
            main_user = User(
                username='santosh ghanwat',
                password=generate_password_hash('ghanwat@187514'),
                role='main'
            )
            db.session.add(main_user)
            db.session.commit()
            print("Main user created successfully")
        else:
            print("Main user already exists")
    except Exception as e:
        print(f"Error creating main user: {e}")
        db.session.rollback()

# Import and register blueprints
from app.controllers.auth_controller import auth_bp
from app.controllers.voter_controller import voter_bp
from app.controllers.user_controller import user_bp

app.register_blueprint(auth_bp)
app.register_blueprint(voter_bp)
app.register_blueprint(user_bp)

if __name__ == '__main__':
    app.run(debug=True)