from flask import flash, redirect, render_template, url_for
from flask.typing import ResponseReturnValue
from flask.views import MethodView
from flask_login import current_user

from app import db
from app.decorators import admin_required
from app.forms import SpaceshipForm
from app.models import Spaceship


class CreateSpaceshipView(MethodView):
    decorators = [admin_required]

    def __init__(self) -> None:
        self.form = SpaceshipForm()

    def get(self) -> ResponseReturnValue:
        return render_template(
            "mission_control/create_object.html", title="Create Spaceship", form=self.form, model_name="Spaceship"
        )

    def post(self) -> ResponseReturnValue:
        form = self.form
        if form.validate_on_submit() and current_user.is_authenticated:
            obj = Spaceship()
            form.populate_obj(obj)
            obj.creator_id = current_user.id
            db.session.add(obj)
            db.session.commit()
            flash("Spaceship Created successfully!", "success")
            return redirect(url_for("mission_control.list_spaceships"))
        return render_template(
            "mission_control/create_object.html", title="Create Spaceship", form=form, model_name="Spaceship"
        )
