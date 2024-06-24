from app.blueprints import main_bp as bp
from app.views.main.index import HomeView
from flask import redirect, url_for


@bp.route("/", methods=["GET"])
def root():
    return redirect(url_for("main.index"))


bp.add_url_rule("/home",
                view_func=HomeView.as_view("index"))
