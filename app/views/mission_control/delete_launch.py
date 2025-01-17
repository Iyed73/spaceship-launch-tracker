from uuid import UUID

from flask import current_app, flash, redirect, url_for
from flask.typing import ResponseReturnValue
from flask.views import MethodView
from flask_login import current_user
from redis.exceptions import RedisError

from app import db
from app.decorators import admin_required
from app.models import Launch, LaunchStatus


class DeleteLaunchView(MethodView):
    decorators = [admin_required]

    @staticmethod
    def notify(launch: Launch) -> None:
        try:
            current_app.task_queue.enqueue(
                "app.tasks.launch_cancellation.process_launch_cancellation_notification", launch_id=launch.id
            )
        except RedisError:
            current_app.logger.exception("Failed to queue launch cancellation notification")
            flash("Subscribers could not be notified about this launch.", "warning")

    def post(self, id: UUID) -> ResponseReturnValue:
        launch = Launch.query.get_or_404(id)
        try:
            launch.status = LaunchStatus.CANCELLED
        except ValueError:
            flash(f"A {launch.status} launch cannot be cancelled.", "danger")
            return redirect(url_for("mission_control.list_launches"))
        launch.record_event(current_user.id)
        db.session.commit()
        self.notify(launch)
        flash("Launch cancelled successfully!", "success")
        return redirect(url_for("mission_control.list_launches"))
