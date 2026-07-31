import json
import os
from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.event_control import EventControl

riddles = Blueprint(
    "riddles",
    __name__,
    url_prefix="/riddles"
)


@riddles.route("/instructions")
def instructions():
    return render_template("riddles_instructions.html")


@riddles.route("/start")
def start():

    event = EventControl.query.first()

    if not event or not event.round2_enabled:
       flash("Round 2 has not started yet.", "warning")
       return redirect(url_for("auth.dashboard"))

    json_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "riddles_questions.json"
    )

    with open(json_path, "r", encoding="utf-8") as file:
        questions = json.load(file)

    return render_template(
        "riddles.html",
        questions=questions
    )

@riddles.route("/complete", methods=["POST"])
@login_required
def complete():

    current_user.is_riddles_completed = True

    db.session.commit()

    return jsonify({
        "success": True
    })