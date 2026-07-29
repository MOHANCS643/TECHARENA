from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models.quiz_control import QuizControl
import json
import os
from datetime import datetime, UTC

quiz = Blueprint(
    "quiz",
    __name__,
    url_prefix="/quiz"
)


# Quiz Page
@quiz.route("/")
@login_required
def quiz_home():

    if session.get("quiz_started"):
       return redirect(url_for("quiz.start_quiz_page"))

    control = QuizControl.query.first()

    if not control:
        return render_template(
            "instructions.html",
            message="Quiz has not started yet. Please wait for the administrator."
        )

    if control.status == "waiting":
        return render_template(
            "instructions.html",
            message="Quiz has not started yet. Please wait for the administrator."
        )

    if control.status == "ended":
        return render_template(
            "instructions.html",
            message="Quiz has ended."
        )

    if control.paused:
        return render_template(
            "instructions.html",
            message="Quiz is temporarily paused."
        )

    return render_template(
    "instructions.html",
    message=None
)

@quiz.route("/start")
@login_required
def start_quiz_page():

    if session.get("quiz_started"):
        return render_template("quiz.html")

    control = QuizControl.query.first()

    if not control:
        return render_template(
            "instructions.html",
            message="Quiz has not started yet."
        )

    if control.status != "running" or control.paused:
        return render_template(
            "instructions.html",
            message="Quiz is not available right now."
        )

    session["quiz_started"] = True
    return render_template("quiz.html")

# API to send questions
@quiz.route("/questions")
@login_required
def get_questions():

    control = QuizControl.query.first()

    if not control or control.status != "running" or control.paused:
        return jsonify([])

    base_dir = os.path.dirname(os.path.dirname(__file__))

    json_path = os.path.join(
        base_dir,
        "data",
        "quiz_questions.json"
    )

    with open(json_path, "r", encoding="utf-8") as file:
        questions = json.load(file)

    return jsonify(questions)


@quiz.route("/submit", methods=["POST"])
@login_required
def submit_quiz():

    if current_user.is_quiz_completed:
       return jsonify({
           "error": "Quiz already submitted."
    }), 400

    user_answers = request.json

    base_dir = os.path.dirname(os.path.dirname(__file__))

    json_path = os.path.join(
        base_dir,
        "data",
        "quiz_questions.json"
    )

    with open(json_path, "r", encoding="utf-8") as file:
        questions = json.load(file)

    score = 0

    results = []

    for i, q in enumerate(questions):

        correct_index = q["options"].index(q["answer"])

        selected = user_answers.get(str(i))

        is_correct = selected == correct_index

        if is_correct:
            score += 1

        results.append({
            "question": q["question"],
            "selected": selected,
            "correct": correct_index,
            "is_correct": is_correct
        })

    current_user.score = score
    current_user.percentage = round((score / len(questions)) * 100, 2)
    current_user.is_quiz_completed = True
    current_user.submitted_at = datetime.now(UTC)

    db.session.commit()
    session.pop("quiz_started", None)

    return jsonify({
        "score": score,
        "total": len(questions),
        "results": results
    })


@quiz.route("/result")
def quiz_result():

    score = request.args.get("score", 0)

    total = request.args.get("total", 0)

    percentage = request.args.get("percentage", "0")

    return render_template(
        "result.html",
        score=score,
        total=total,
        percentage=percentage
    )