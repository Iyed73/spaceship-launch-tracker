from flask.views import MethodView
from flask import render_template, flash, url_for, redirect, request
from flask_login import current_user
from app.models import LaunchSite
from app.forms import LaunchSiteForm
from app import db
from app.decorators import admin_required


class UpdateLaunchSiteView(MethodView):
    decorators = [admin_required]

    def __init__(self):
        self.form = LaunchSiteForm()

    def get(self, id):
        launch_site = LaunchSite.query.get_or_404(id)
        self.form.process(obj=launch_site)
        return render_template(
            "mission_control/update_object.html",
            title="Update Launch Site",
            form=self.form,
            model_name="Launch Site")

    def post(self, id):
        launch_site = LaunchSite.query.get_or_404(id)
        if self.form.validate_on_submit():
            self.form.populate_obj(launch_site)
            launch_site.creator_id = current_user.id
            db.session.commit()
            flash("Launch Site updated successfully!", "success")
            return redirect(url_for("mission_control.list_launchsites"))
        return render_template(
            "mission_control/update_object.html",
            title="Update Launch Site",
            form=self.form,
            model_name="Launch Site")
