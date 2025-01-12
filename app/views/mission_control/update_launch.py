from flask.views import MethodView
from flask import render_template, flash, url_for, redirect
from flask_login import current_user
from app.models import Launch, Spaceship, LaunchSite
from app.forms import LaunchUpdateForm
from app import db
from app.decorators import admin_required
from flask import current_app
from redis.exceptions import RedisError
from sqlalchemy.orm.exc import StaleDataError


class UpdateLaunchView(MethodView):
    decorators = [admin_required]

    def __init__(self):
        self.form = LaunchUpdateForm()
        self.form.spaceship_id.choices = [(spaceship.id, spaceship.name) for spaceship in Spaceship.query.all()]
        self.form.launch_site_id.choices = [(site.id, site.name) for site in LaunchSite.query.all()]

    @staticmethod
    def notify(launch):
        try:
            current_app.task_queue.enqueue(f"app.tasks.launch_update.process_launch_update_notification",
                                           launch_id=launch.id)
        except RedisError:
            current_app.logger.exception("Failed to queue launch update notification")
            flash("Subscribers could not be notified about this launch.", "warning")

    def get_launch(self, id):
        launch = Launch.query.get_or_404(id)
        self.form.status.choices = [(status.value, status.value.capitalize())
                                    for status in (launch.status, *launch.status.transitions)]
        return launch

    def get(self, id):
        launch = self.get_launch(id)
        self.form.process(obj=launch)
        return render_template(
            "mission_control/update_object.html",
            title="Update Launch",
            form=self.form,
            model_name="Launch")

    def post(self, id):
        launch = self.get_launch(id)
        if self.form.validate_on_submit():
            try:
                if self.form.version.data != launch.version:
                    raise StaleDataError
                self.form.populate_obj(launch)
                changed = launch.record_event(current_user.id)
                db.session.commit()
            except StaleDataError:
                db.session.rollback()
                flash("Launch was modified by someone else, please review the latest version.", "danger")
                return redirect(url_for("mission_control.update_launch", id=id))
            if changed:
                self.notify(launch)
            flash("Launch updated successfully!", "success")
            return redirect(url_for("mission_control.list_launches"))
        return render_template(
            "mission_control/update_object.html",
            title="Update Launch",
            form=self.form,
            model_name="Launch")
