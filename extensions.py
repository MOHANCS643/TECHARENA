from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Database Object
db = SQLAlchemy()

# Login Manager
login_manager = LoginManager()

# Redirect to login page if user is not logged in
login_manager.login_view = "auth.login"

# Message when login is required
login_manager.login_message = "Please login to continue."

# Message category
login_manager.login_message_category = "warning"