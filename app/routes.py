from flask import render_template

from app import app


@app.route("/index")
def hello() -> str:
    return render_template("base.html")
