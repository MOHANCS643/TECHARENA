from flask import Blueprint, render_template

# Create Blueprint
home = Blueprint("home", __name__)


# Home Page
@home.route("/")
def index():
    return render_template("index.html")


# Instructions Page
@home.route("/instructions")
def instructions():
    return render_template("instructions.html")


# Leaderboard Page
@home.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")
