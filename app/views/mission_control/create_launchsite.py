from flask.views import MethodView
from flask import render_template, flash, url_for, redirect
from flask_login import current_user
from app.models import LaunchSite
from app.forms import LaunchSiteForm
from app import db
from app.decorators import admin_required


class CreateLaunchSiteView(MethodView):
    decorators = [admin_required]

    def __init__(self):
        self.form = LaunchSiteForm()

    def get(self):
        return render_template("mission_control/create_object.html",
                               title="Create Launch Site",
                               form=self.form,
                               model_name="Launch Site")

    def post(self):
        form = self.form
        if form.validate_on_submit() and current_user.is_authenticated:
            obj = LaunchSite()
            form.populate_obj(obj)
            obj.creator_id = current_user.id
            db.session.add(obj)
            db.session.commit()
            flash("Launch Site Created successfully!", "success")
            return redirect(url_for("mission_control.list_launchsites"))
        return render_template("mission_control/create_object.html",
                               title="Create Launch Site",
                               form=form,
                               model_name="Launch Site")
