from flask.views import MethodView
from flask import render_template, flash, url_for, redirect
from flask_login import current_user
from app.models import Launch, Spaceship, LaunchSite
from app.forms import LaunchForm
from app import db
from app.decorators import admin_required
from flask import current_app


class CreateLaunchView(MethodView):
    decorators = [admin_required]

    def __init__(self):
        self.form = LaunchForm()
        self.form.spaceship_id.choices = [(spaceship.id, spaceship.name) for spaceship in Spaceship.query.all()]
        self.form.launch_site_id.choices = [(site.id, site.name) for site in LaunchSite.query.all()]

    @staticmethod
    def notify(launch):
        current_app.task_queue.enqueue(f"app.tasks.launch_creation.process_launch_creation_notification", launch=launch)

    def get(self):
        return render_template("mission_control/create_object.html",
                               title="Create Launch",
                               form=self.form,
                               model_name="Launch")

    def post(self):
        form = self.form
        if form.validate_on_submit() and current_user.is_authenticated:
            launch = Launch()
            form.populate_obj(launch)
            launch.creator_id = current_user.id
            db.session.add(launch)
            db.session.commit()
            self.notify(launch)
            flash("Launch Created successfully!", "success")
            return redirect(url_for("mission_control.list_launches"))
        return render_template("mission_control/create_object.html",
                               title="Create Launch",
                               form=form,
                               model_name="Launch")
