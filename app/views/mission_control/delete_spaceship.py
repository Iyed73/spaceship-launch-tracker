from flask import redirect, url_for, flash
from flask.views import MethodView
from app.models import Spaceship
from app import db
from app.decorators import admin_required


class DeleteSpaceshipView(MethodView):
    decorators = [admin_required]

    def post(self, id):
        obj = Spaceship.query.get_or_404(id)
        db.session.delete(obj)
        db.session.commit()
        flash("Spaceship deleted successfully!", "success")
        return redirect(url_for("mission_control.list_spaceships"))
