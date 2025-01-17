from flask import redirect, url_for
from flask.typing import ResponseReturnValue

from app.blueprints import main_bp as bp
from app.views.main.index import HomeView


@bp.route("/", methods=["GET"])
def root() -> ResponseReturnValue:
    return redirect(url_for("main.index"))


bp.add_url_rule("/home", view_func=HomeView.as_view("index"))
