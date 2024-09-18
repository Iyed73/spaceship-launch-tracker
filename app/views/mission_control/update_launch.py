from flask.views import MethodView
from flask import render_template, flash, url_for, redirect, request
from flask_login import current_user
from app.models import Launch, Spaceship, LaunchSite, LaunchEvent
from app.forms import LaunchForm
from app import db
from app.decorators import admin_required
from flask import current_app
from app.tasks.process_event import process_subscribers_event
from app.tasks.event_categories import EventCategory


class UpdateLaunchView(MethodView):
    decorators = [admin_required]

    def __init__(self):
        self.form = LaunchForm()
        self.form.spaceship_id.choices = [(spaceship.id, spaceship.name) for spaceship in Spaceship.query.all()]
        self.form.launch_site_id.choices = [(site.id, site.name) for site in LaunchSite.query.all()]

    @staticmethod
    def create_event(launch):
        job = current_app.task_queue.enqueue(process_subscribers_event, EventCategory.LAUNCH_UPDATE, launch=launch)
        event = LaunchEvent(id=job.get_id(), name=f"update launch: {launch.mission}", launch=launch, category=EventCategory.LAUNCH_UPDATE)
        db.session.add(event)
        db.session.commit()

    def get(self, id):
        launch = Launch.query.get_or_404(id)
        self.form.process(obj=launch)
        return render_template(
            "mission_control/update_object.html",
            title="Update Launch",
            form=self.form,
            model_name="Launch")

    def post(self, id):
        launch = Launch.query.get_or_404(id)
        if self.form.validate_on_submit():
            self.form.populate_obj(launch)
            launch.creator_id = current_user.id
            db.session.commit()
            self.create_event(launch)
            flash("Launch updated successfully!", "success")
            return redirect(url_for("mission_control.list_launches"))
        return render_template(
            "mission_control/update_object.html",
            title="Update Launch",
            form=self.form,
            model_name="Launch")
