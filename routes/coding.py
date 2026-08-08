from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from extensions import db
from models.coding_submission import CodingSubmission
from models.event_control import EventControl
import subprocess
import tempfile
import os
import json
import shutil
from models.team import Team
from datetime import datetime

coding_bp = Blueprint("coding", __name__)

@coding_bp.route("/coding/instructions")
@login_required
def coding_instructions():
    return render_template("coding_instructions.html")

@coding_bp.route("/coding")
@login_required
def coding_page():

    question_id = request.args.get("q", 1, type=int)

    json_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "coding_question.json"
    )

    with open(json_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    total_questions = len(questions)

    if question_id < 1:
        question_id = 1

    if question_id > total_questions:
        question_id = total_questions

    question = questions[question_id - 1]

    return render_template(
        "coding.html",
        question=question,
        current_question=question_id,
        total_questions=total_questions
    )

@coding_bp.route("/coding/submit", methods=["POST"])
@login_required
def submit_code():

    code = request.json.get("code")

    if not code:
        return jsonify({
            "success": False,
            "message": "Code cannot be empty."
        })

    submission = CodingSubmission.query.filter_by(
        team_id=current_user.id
    ).first()

    if submission:

        submission.code = code

    else:

        submission = CodingSubmission(
            team_id=current_user.id,
            code=code
        )

        db.session.add(submission)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Code submitted successfully."
    })

@coding_bp.route("/round3_status")
@login_required
def round3_status():

    control = EventControl.query.first()

    if control:
        return jsonify({
            "enabled": control.round3_enabled
        })

    return jsonify({
        "enabled": False
    })

def execute_code(language, code, custom_input):

    language = str(language).strip().lower()

    if language == "python":
        language = "Python"
    elif language == "c":
        language = "C"
    elif language in ("cpp", "c++"):
        language = "C++"
    elif language == "java":
        language = "Java"

    temp_dir = tempfile.mkdtemp()

    try:

        # ---------------- Python ----------------
        if language == "Python":

            filename = os.path.join(temp_dir, "main.py")

            with open(filename, "w", encoding="utf-8") as f:
                f.write(code)

            command = ["python", filename]

        # ---------------- C ----------------
        elif language == "C":

            source = os.path.join(temp_dir, "main.c")
            exe = os.path.join(temp_dir, "main.exe")

            with open(source, "w", encoding="utf-8") as f:
                f.write(code)

            compile_result = subprocess.run(
                ["gcc", source, "-o", exe],
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                return False, compile_result.stderr

            command = [exe]

        # ---------------- C++ ----------------
        elif language == "C++":

            source = os.path.join(temp_dir, "main.cpp")
            exe = os.path.join(temp_dir, "main.exe")

            with open(source, "w", encoding="utf-8") as f:
                f.write(code)

            compile_result = subprocess.run(
                ["g++", source, "-o", exe],
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                return False, compile_result.stderr

            command = [exe]

        # ---------------- Java ----------------
        elif language == "Java":

            source = os.path.join(temp_dir, "Main.java")

            with open(source, "w", encoding="utf-8") as f:
                f.write(code)

            compile_result = subprocess.run(
                ["javac", source],
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                return False, compile_result.stderr

            command = [
                "java",
                "-cp",
                temp_dir,
                "Main"
            ]

        else:

            return False, "Unsupported Language: " + str(language)

        result = subprocess.run(
            command,
            input=custom_input,
            capture_output=True,
            text=True,
            timeout=5
        )

        output = result.stdout if result.stdout else result.stderr

        return True, output

    except subprocess.TimeoutExpired:

        return False, "Execution Timeout (5 seconds)"

    except Exception as e:

        return False, str(e)

    finally:

        shutil.rmtree(temp_dir, ignore_errors=True)

@coding_bp.route("/coding/run", methods=["POST"])
@login_required
def run_code():

    
    code = request.json.get("code", "")
    custom_input = request.json.get("input", "")

    language = request.json.get("language", "python")

    language_map = {
    "python": "Python",
    "c": "C",
    "cpp": "C++",
    "java": "Java"
    }

    language = language_map.get(language.lower(), language)

    if not code.strip():

        return jsonify({
            "success": False,
            "output": "No code entered."
        })

    try:

        current_question = int(
            request.json.get("current_question", 1)
        )

        json_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "coding_question.json"
        )

        with open(json_path, "r", encoding="utf-8") as f:
            questions = json.load(f)

        question = questions[current_question - 1]

        # SQL Question
        if question.get("type") == "sql":

            return jsonify({
                "success": True,
                "output": "⚠️ SQL Question\n\nUse Final Submit to submit this query."
            })

        # Execute Code
        success, output = execute_code(
            language,
            code,
            custom_input
        )
        print("Language received:", language)

        if not success:

            return jsonify({
                "success": False,
                "output": output
            })

        if "EOFError" in output:

            return jsonify({
                "success": False,
                "output": "⚠️ Please enter the required input in the Custom Input box."
            })

        return jsonify({
            "success": True,
            "output": output
        })

    except subprocess.TimeoutExpired:

        return jsonify({
            "success": False,
            "output": "Execution Timeout (5 seconds)"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "output": str(e)
        })


@coding_bp.route("/coding/judge", methods=["POST"])
@login_required
def judge_code():

    try:

        data = request.json

        language = data.get("language", "Python")

        # Each question can be solved in a different language.
        # The frontend sends qN_language for every question.
        codes = [
            data.get("q1", ""),
            data.get("q2", ""),
            data.get("q3", ""),
            data.get("q4", ""),
            data.get("q5", "")
        ]

        languages = [
            data.get("q1_language") or language,
            data.get("q2_language") or language,
            data.get("q3_language") or language,
            data.get("q4_language") or language,
            data.get("q5_language") or language
        ]

        json_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "coding_question.json"
        )

        with open(json_path, "r", encoding="utf-8") as f:
            questions = json.load(f)

        submission = CodingSubmission.query.filter_by(
            team_id=current_user.id
        ).first()

        if not submission:

            submission = CodingSubmission(
                team_id=current_user.id
            )

            db.session.add(submission)

        total_score = 0

        for i, question in enumerate(questions):

            code = codes[i].strip()

            if not code:
                continue

            # ---------------------------------
            # SQL Question
            # ---------------------------------

            if question.get("type") == "sql":

                total_score += 20
                continue

            hidden_tests = question.get("hidden_tests", [])

            passed = 0

            # ---------------------------------
            # Run every hidden test
            # using selected language
            # ---------------------------------

            for test in hidden_tests:

                test_input = test.get("input", "")
                expected_output = test.get("output", "").strip()

                success, output = execute_code(
                    languages[i],
                    code,
                    test_input
                )

                if not success:
                    continue

                actual_output = output.strip()

                if actual_output == expected_output:

                    passed += 1

            # ---------------------------------
            # Give 20 marks only if
            # ALL hidden tests pass
            # ---------------------------------

            if hidden_tests and passed == len(hidden_tests):

                total_score += 20

        # ---------------------------------
        # Save all answers
        # ---------------------------------

        submission.code_q1 = codes[0]
        submission.code_q2 = codes[1]
        submission.code_q3 = codes[2]
        submission.code_q4 = codes[3]
        submission.code_q5 = codes[4]

        # Keep the selected/current language for compatibility with the
        # existing database schema. Per-question languages are used for judging.
        submission.language = language
        submission.score = total_score
        submission.submitted = True
        submission.status = "Completed"

        current_user.is_coding_completed = True
        current_user.score = total_score

        submission.submitted_at = datetime.now()

        db.session.commit()

        return jsonify({

            "success": True,

            "message": "Final Submission Successful",

            "score": total_score

        })

    except Exception as e:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message": str(e)

        })
    
@coding_bp.route("/coding/leaderboard")
@login_required
def coding_leaderboard():

    if not session.get("admin"):
        return jsonify({"success": False}), 401

    submissions = (
        db.session.query(CodingSubmission, Team)
        .join(Team, CodingSubmission.team_id == Team.id)
        .filter(CodingSubmission.submitted == True)
        .order_by(
            CodingSubmission.score.desc(),
            CodingSubmission.submitted_at.asc()
        )
        .all()
    )

    data = []

    rank = 1

    for submission, team in submissions:

        data.append({

            "rank": rank,

            "team": team.team_name,

            "college": team.college_name,

            "score": submission.score,

            "status": submission.status,

            "time": submission.submitted_at.strftime("%I:%M %p")
                   if submission.submitted_at else "-"

        })

        rank += 1

    return jsonify(data)

@coding_bp.route("/coding/leaderboard/view")
@login_required
def coding_leaderboard_page():

    return render_template("coding_leaderboard.html")

