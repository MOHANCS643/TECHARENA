from extensions import db
from datetime import datetime


class CodingSubmission(db.Model):
    __tablename__ = "coding_submissions"

    id = db.Column(db.Integer, primary_key=True)

    team_id = db.Column(
        db.Integer,
        db.ForeignKey("teams.id"),
        nullable=False
    )

    language = db.Column(
        db.String(50),
        default="Python"
    )

    code_q1 = db.Column(db.Text, default="")
    code_q2 = db.Column(db.Text, default="")
    code_q3 = db.Column(db.Text, default="")
    code_q4 = db.Column(db.Text, default="")
    code_q5 = db.Column(db.Text, default="")

    submitted = db.Column(
        db.Boolean,
        default=False
    )

    # NEW
    passed = db.Column(
        db.Integer,
        default=0
    )

    total = db.Column(
        db.Integer,
        default=0
    )

    score = db.Column(
        db.Integer,
        default=0
    )

    status = db.Column(
        db.String(30),
        default="Pending"
    )

    submitted_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )