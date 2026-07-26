from extensions import db
from datetime import datetime

class QuizControl(db.Model):

    __tablename__ = "quiz_control"

    id = db.Column(db.Integer, primary_key=True)

    status = db.Column(db.String(20), default="waiting")

    duration = db.Column(db.Integer, default=20)

    started_at = db.Column(db.DateTime)

    paused = db.Column(db.Boolean, default=False)

    remaining_seconds = db.Column(db.Integer, default=1200)