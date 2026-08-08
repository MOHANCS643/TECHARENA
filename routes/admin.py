from flask import Blueprint, render_template, request, redirect, session
from models.team import Team
from flask import jsonify
from sqlalchemy import desc
from models.quiz_control import QuizControl
from models.event_control import EventControl
from extensions import db
from datetime import datetime
from models.coding_submission import CodingSubmission
admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "techarena"


@admin.route("/login")
def login():
    return render_template("admin_login.html")


@admin.route("/login", methods=["POST"])
def login_post():

    username = request.form["username"]
    password = request.form["password"]

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

       session["admin"] = True

    # Reset all teams to offline
       Team.query.update({
           Team.is_online: False
        })
    db.session.commit()

    return redirect("/admin/dashboard")

    return render_template(
        "admin_login.html",
        error="Invalid Username or Password"
    )


@admin.route("/dashboard")
def dashboard():

    if not session.get("admin"):
        return redirect("/admin/login")

    teams = Team.query.order_by(
        Team.score.desc(),
        Team.percentage.desc(),
        Team.submitted_at.asc()
    ).all()

    return render_template(
        "admin_dashboard.html",
        teams=teams
    )

@admin.route("/stats")
def stats():

    if not session.get("admin"):
        return jsonify({"error": "Unauthorized"}), 401

    # ==========================
    # Quiz Leaderboard
    # ==========================
    teams = Team.query.filter_by(
        is_quiz_completed=True
    ).order_by(
        Team.score.desc(),
        Team.percentage.desc(),
        Team.submitted_at.asc()
    ).all()

    total_teams = Team.query.count()

    submitted = Team.query.filter_by(
        is_quiz_completed=True
    ).count()

    online = Team.query.filter_by(
        is_online=True
    ).count()

    running = total_teams - submitted

    highest = teams[0].score if teams else 0

    leaderboard = []

    rank = 1

    for team in teams:

        leaderboard.append({

            "rank": rank,

            "team_name": team.team_name,

            "college": team.college_name,

            "score": team.score,

            "percentage": team.percentage

        })

        rank += 1

    # ==========================
    # Online Teams
    # ==========================
    online_teams = []

    for team in Team.query.filter_by(is_online=True).all():

        online_teams.append({

            "team_name": team.team_name,

            "college": team.college_name,

            "login_time": team.login_time.strftime("%I:%M %p") if team.login_time else "-"

        })

    # ==========================
    # Coding Leaderboard
    # ==========================
    coding_submissions = (
        db.session.query(CodingSubmission, Team)
        .join(Team, CodingSubmission.team_id == Team.id)
        .filter(CodingSubmission.submitted == True)
        .order_by(
            CodingSubmission.score.desc(),
            CodingSubmission.submitted_at.asc()
        )
        .all()
    )

    coding_leaderboard = []

    rank = 1

    for submission, team in coding_submissions:

        coding_leaderboard.append({

            "rank": rank,

            "team": team.team_name,

            "college": team.college_name,

            "score": submission.score,

            "status": submission.status

        })

        rank += 1

    return jsonify({

        "total_teams": total_teams,

        "online": online,

        "online_teams": online_teams,

        "submitted": submitted,

        "running": running,

        "highest": highest,

        "leaderboard": leaderboard,

        "coding_leaderboard": coding_leaderboard

    })

@admin.route("/logout")
def logout():

    session.clear()

    return redirect("/admin/login")

@admin.route("/start_quiz", methods=["POST"])
def start_quiz():

    if not session.get("admin"):
        return jsonify({"success": False}), 401

    quiz = QuizControl.query.first()

    if not quiz:
        quiz = QuizControl()
        db.session.add(quiz)

    quiz.status = "running"

    quiz.started_at = datetime.now()

    quiz.paused = False

# If duration is empty, use 20 minutes
    if not quiz.duration:
       quiz.duration = 20

    quiz.remaining_seconds = quiz.duration * 60

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Quiz Started Successfully"
    })


@admin.route("/pause_quiz", methods=["POST"])
def pause_quiz():

    if not session.get("admin"):
        return jsonify({"success": False}), 401

    quiz = QuizControl.query.first()

    if quiz:
        quiz.paused = not quiz.paused
        db.session.commit()

    return jsonify({"success": True})

@admin.route("/end_quiz", methods=["POST"])
def end_quiz():

    if not session.get("admin"):
        return jsonify({"success":False}),401

    quiz = QuizControl.query.first()

    if quiz:
        quiz.status="ended"
        quiz.paused=False
        db.session.commit()

    return jsonify({"success":True})

@admin.route("/reset_quiz", methods=["POST"])
def reset_quiz():

    if not session.get("admin"):
        return jsonify({"success":False}),401

    quiz=QuizControl.query.first()

    if quiz:

        quiz.status="waiting"
        quiz.started_at=None
        quiz.paused=False

    Team.query.update({

    Team.score: 0,
    Team.percentage: 0,
    Team.is_quiz_completed: False,
    Team.submitted_at: None,
    Team.is_online: False

})

    db.session.commit()

    return jsonify({"success":True})

@admin.route("/quiz_status")
def quiz_status():

    quiz = QuizControl.query.first()

    if not quiz:

        return jsonify({

            "status":"waiting",
            "paused":False

        })

    return jsonify({

        "status":quiz.status,
        "paused":quiz.paused

    })

@admin.route("/countdown")
def countdown():

    quiz = QuizControl.query.first()

    if not quiz:

        return jsonify({
            "remaining": 0,
            "status": "waiting"
        })

    if quiz.status != "running":

        return jsonify({
            "remaining": quiz.remaining_seconds,
            "status": quiz.status
        })

    if not quiz.paused:

        elapsed = int(
            (datetime.now() - quiz.started_at).total_seconds()
        )

        remaining = max(
            quiz.duration * 60 - elapsed,
            0
        )

        quiz.remaining_seconds = remaining

        if remaining == 0:
            quiz.status = "ended"

        db.session.commit()

    return jsonify({

        "remaining": quiz.remaining_seconds,

        "status": quiz.status,

        "paused": quiz.paused

    })

@admin.route("/enable_round2", methods=["POST"])
def enable_round2():

    if not session.get("admin"):
        return jsonify({"success": False}), 401

    event = EventControl.query.first()

    if not event:
        event = EventControl(id=1)
        db.session.add(event)

    event.round2_enabled = True
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Round 2 Enabled"
    })


@admin.route("/disable_round2", methods=["POST"])
def disable_round2():

    if not session.get("admin"):
        return jsonify({"success": False}), 401

    event = EventControl.query.first()

    if event:
        event.round2_enabled = False
        db.session.commit()

    return jsonify({
        "success": True,
        "message": "Round 2 Disabled"
    })

@admin.route("/reset_round2", methods=["POST"])
def reset_round2():

    if not session.get("admin"):
        return jsonify({"success": False}), 401

    # Lock Round 2
    event = EventControl.query.first()

    if event:
        event.round2_enabled = False

    # Reset every team
    Team.query.update({
        Team.is_riddles_completed: False
    })

    db.session.commit()

    return jsonify({
        "success": True
    })

@admin.route("/enable_round3", methods=["POST"])
def enable_round3():

    control = EventControl.query.first()

    if not control:
        control = EventControl()
        db.session.add(control)

    control.round3_enabled = True

    db.session.commit()

    return jsonify(success=True)

@admin.route("/disable_round3", methods=["POST"])
def disable_round3():

    control = EventControl.query.first()

    if control:
        control.round3_enabled = False
        db.session.commit()

    return jsonify(success=True)

@admin.route("/reset_round3", methods=["POST"])
def reset_round3():

    if not session.get("admin"):
        return jsonify({"success": False}), 401

    # Disable Round 3
    control = EventControl.query.first()

    if control:
        control.round3_enabled = False

    # Reset every team
    Team.query.update({
        Team.is_coding_completed: False
    })

    # Reset every coding submission
    CodingSubmission.query.update({

        CodingSubmission.language: "Python",

        CodingSubmission.code_q1: "",

        CodingSubmission.code_q2: "",

        CodingSubmission.code_q3: "",

        CodingSubmission.code_q4: "",

        CodingSubmission.code_q5: "",

        CodingSubmission.submitted: False,

        CodingSubmission.passed: 0,

        CodingSubmission.total: 0,

        CodingSubmission.score: 0,

        CodingSubmission.status: "Pending",

        CodingSubmission.submitted_at: None

    })

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Round 3 Reset Successfully"
    })