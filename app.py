from flask import Flask
from config import Config
from extensions import db, login_manager

# Import Blueprints
from routes.home import home
from routes.auth import auth
from routes.quiz import quiz
from routes.coding import coding
from routes.admin import admin
from routes.api import api
from routes.riddles import riddles


def create_app():
    app = Flask(__name__)

    # Load Configuration
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    app.register_blueprint(home)
    app.register_blueprint(auth)
    app.register_blueprint(quiz)
    app.register_blueprint(riddles)
    app.register_blueprint(coding)
    app.register_blueprint(admin)
    app.register_blueprint(api)

    # Create Database Tables
    with app.app_context():
        db.create_all()

    return app


# Create Application
app = create_app()


# Run Server
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )