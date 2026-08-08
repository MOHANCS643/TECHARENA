from flask import Blueprint

from models.event_control import EventControl

api = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)

@api.route("/round3_status")
def round3_status():

    control = EventControl.query.first()

    return {
        "enabled": control.round3_enabled if control else False
    }