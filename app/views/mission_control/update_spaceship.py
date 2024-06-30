from flask.views import MethodView
from flask import render_template, flash, url_for, redirect, request
from flask_login import current_user
from app.models import Spaceship
from app.forms import SpaceshipForm
from app import db
from app.decorators import admin_required


class UpdateSpaceshipView(MethodView):
    decorators = [admin_required]

    def __init__(self):
        self.form = SpaceshipForm()

    def get(self, id):
        spaceship = Spaceship.query.get_or_404(id)
        self.form.process(obj=spaceship)
        return render_template(
            "mission_control/update_object.html",
            title="Update Spaceship",
            form=self.form,
            model_name="Launch Site")

    def post(self, id):
        spaceship = Spaceship.query.get_or_404(id)
        if self.form.validate_on_submit():
            self.form.populate_obj(spaceship)
            spaceship.creator_id = current_user.id
            db.session.commit()
            flash("Spaceship updated successfully!", "success")
            return redirect(url_for("mission_control.list_spaceships"))
        return render_template(
            "mission_control/update_object.html",
            title="Update Spaceship",
            form=self.form,
            model_name="Spaceship")
