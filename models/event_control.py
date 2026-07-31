from extensions import db

class EventControl(db.Model):
    __tablename__ = "event_control"

    id = db.Column(db.Integer, primary_key=True)
    round2_enabled = db.Column(db.Boolean, default=False)