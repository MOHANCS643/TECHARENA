from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.team import Team
from extensions import db
import random
import string
from datetime import datetime
from models.event_control import EventControl

auth = Blueprint("auth", __name__)


def generate_team_id():
    while True:
        team_id = "TA" + str(random.randint(1000, 9999))
        if not Team.query.filter_by(team_id=team_id).first():
            return team_id


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        team_name = request.form.get("team_name")
        college_name = request.form.get("college_name")
        leader_name = request.form.get("leader_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")

        # Check email already exists
        if Team.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("auth.register"))

        team = Team(
            team_id=generate_team_id(),
            team_name=team_name,
            college_name=college_name,
            leader_name=leader_name,
            email=email,
            phone=phone
        )

        team.set_password(password)

        db.session.add(team)
        db.session.commit()

        flash("Registration Successful! Please Login.", "success")

        return redirect(url_for("auth.login"))

    return render_template("register.html")

# -----------------------------
# Team Login
# -----------------------------
@auth.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        team = Team.query.filter_by(email=email).first()

        if team and team.check_password(password):

            login_user(team)

            team.is_online = True 

            team.login_time = datetime.now()

            db.session.commit()

            flash("Login Successful!", "success")

            return redirect(url_for("auth.dashboard"))

        flash("Invalid Email or Password!", "danger")

    return render_template("login.html")


# -----------------------------
# Dashboard
# -----------------------------
@auth.route("/dashboard")
@login_required
def dashboard():

    event = EventControl.query.first()

    return render_template(
       "dashboard.html",
        team=current_user,
        event=event
    )

@auth.route("/round2_status")
@login_required
def round2_status():

    event = EventControl.query.first()

    return {
        "enabled": event.round2_enabled if event else False,
        "completed": current_user.is_riddles_completed
    }
# -----------------------------
# Logout
# -----------------------------
@auth.route("/logout")
@login_required
def logout():

    current_user.is_online = False
    current_user.login_time = None

    db.session.commit()

    logout_user()

    flash("Logged out successfully.", "success")

    return redirect(url_for("home.index"))