from flask import Blueprint, render_template

coding = Blueprint(
    "coding",
    __name__,
    url_prefix="/coding"
)


@coding.route("/")
def coding_home():
    return render_template("coding.html")