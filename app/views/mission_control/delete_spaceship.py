from flask import flash, redirect, url_for
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from app import db
from app.decorators import admin_required
from app.models import Spaceship


class DeleteSpaceshipView(MethodView):
    decorators = [admin_required]

    def post(self, id: int) -> ResponseReturnValue:
        obj = Spaceship.query.get_or_404(id)
        db.session.delete(obj)
        db.session.commit()
        flash("Spaceship deleted successfully!", "success")
        return redirect(url_for("mission_control.list_spaceships"))
