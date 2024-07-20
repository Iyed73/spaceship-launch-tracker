from flask.views import MethodView
from flask import render_template, flash, url_for, redirect
from flask_login import current_user
from app.models import Launch, Spaceship, LaunchSite, LaunchEvent
from app.forms import LaunchForm
from app import db
from app.decorators import admin_required
from flask import current_app
from app.tasks.process_event import process_subscribers_event
from app.tasks.event_categories import EventCategory


class CreateLaunchView(MethodView):
    decorators = [admin_required]

    def __init__(self):
        self.form = LaunchForm()
        self.form.spaceship_id.choices = [(spaceship.id, spaceship.name) for spaceship in Spaceship.query.all()]
        self.form.launch_site_id.choices = [(site.id, site.name) for site in LaunchSite.query.all()]

    @staticmethod
    def create_event(launch):
        job = current_app.task_queue.enqueue(process_subscribers_event, EventCategory.NEW_LAUNCH, launch=launch)
        event = LaunchEvent(id=job.get_id(), name=f"new launch: {launch.mission}", launch=launch, category=EventCategory.NEW_LAUNCH)
        db.session.add(event)
        db.session.commit()

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
            self.create_event(launch)
            flash("Launch Created successfully!", "success")
            return redirect(url_for("mission_control.list_launches"))
        return render_template("mission_control/create_object.html",
                               title="Create Launch",
                               form=form,
                               model_name="Launch")
