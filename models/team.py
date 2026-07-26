from extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Team(UserMixin, db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)

    team_id = db.Column(db.String(20), unique=True, nullable=False)

    team_name = db.Column(db.String(100), nullable=False)

    college_name = db.Column(db.String(150), nullable=False)

    leader_name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    phone = db.Column(db.String(15), nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    score = db.Column(db.Integer, default=0)

    percentage = db.Column(db.Float, default=0)

    is_quiz_completed = db.Column(db.Boolean, default=False)

    is_coding_completed = db.Column(db.Boolean, default=False)

    is_online = db.Column(db.Boolean, default=False)

    submitted_at = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<Team {self.team_name}>"

@login_manager.user_loader
def load_user(user_id):
    return Team.query.get(int(user_id))