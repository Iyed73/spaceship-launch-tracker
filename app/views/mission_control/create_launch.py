from flask import current_app, flash, redirect, render_template, url_for
from flask.typing import ResponseReturnValue
from flask.views import MethodView
from flask_login import current_user
from redis.exceptions import RedisError

from app import db
from app.decorators import admin_required
from app.forms import LaunchForm
from app.models import Launch, LaunchSite, LaunchStatus, Spaceship


class CreateLaunchView(MethodView):
    decorators = [admin_required]

    def __init__(self) -> None:
        self.form = LaunchForm()
        self.form.spaceship_id.choices = [(spaceship.id, spaceship.name) for spaceship in Spaceship.query.all()]
        self.form.launch_site_id.choices = [(site.id, site.name) for site in LaunchSite.query.all()]

    @staticmethod
    def notify(launch: Launch) -> None:
        try:
            current_app.task_queue.enqueue(
                "app.tasks.launch_creation.process_launch_creation_notification", launch_id=launch.id
            )
        except RedisError:
            current_app.logger.exception("Failed to queue launch creation notification")
            flash("Subscribers could not be notified about this launch.", "warning")

    def get(self) -> ResponseReturnValue:
        return render_template(
            "mission_control/create_object.html", title="Create Launch", form=self.form, model_name="Launch"
        )

    def post(self) -> ResponseReturnValue:
        form = self.form
        if form.validate_on_submit() and current_user.is_authenticated:
            launch = Launch(status=LaunchStatus.SCHEDULED)
            form.populate_obj(launch)
            launch.creator_id = current_user.id
            launch.record_event(current_user.id)
            db.session.add(launch)
            db.session.commit()
            self.notify(launch)
            flash("Launch Created successfully!", "success")
            return redirect(url_for("mission_control.list_launches"))
        return render_template(
            "mission_control/create_object.html", title="Create Launch", form=form, model_name="Launch"
        )
