from flask.views import MethodView
from flask import render_template, flash, url_for, redirect
from flask_login import current_user
from app.models import Spaceship
from app.forms import SpaceshipForm
from app import db
from app.decorators import admin_required


class CreateSpaceshipView(MethodView):
    decorators = [admin_required]

    def __init__(self):
        self.form = SpaceshipForm()

    def get(self):
        return render_template("mission_control/create_object.html",
                               title="Create Spaceship",
                               form=self.form,
                               model_name="Spaceship")

    def post(self):
        form = self.form
        if form.validate_on_submit() and current_user.is_authenticated:
            obj = Spaceship()
            form.populate_obj(obj)
            obj.creator_id = current_user.id
            db.session.add(obj)
            db.session.commit()
            flash("Spaceship Created successfully!", "success")
            return redirect(url_for("mission_control.list_spaceships"))
        return render_template("mission_control/create_object.html",
                               title="Create Spaceship",
                               form=form,
                               model_name="Spaceship")
