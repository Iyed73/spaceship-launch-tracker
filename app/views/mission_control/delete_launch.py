from flask import redirect, url_for, flash
from flask.views import MethodView
from flask_login import current_user
from app.models import Launch, LaunchStatus
from app import db
from flask import current_app
from app.decorators import admin_required


class DeleteLaunchView(MethodView):
    decorators = [admin_required]

    @staticmethod
    def notify(launch):
        current_app.task_queue.enqueue(f"app.tasks.launch_cancellation.process_launch_cancellation_notification",
                                       launch_id=launch.id)

    def post(self, id):
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
