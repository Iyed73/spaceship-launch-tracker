from flask import redirect, url_for, flash
from flask.views import MethodView
from app.models import Launch
from app import db
from flask import current_app
from app.decorators import admin_required


class DeleteLaunchView(MethodView):
    decorators = [admin_required]

    @staticmethod
    def notify(launch):
        current_app.task_queue.enqueue(f"app.tasks.launch_cancellation.process_launch_cancellation_notification", launch=launch)

    def post(self, id):
        launch = Launch.query.get_or_404(id)
        db.session.delete(launch)
        db.session.commit()
        self.notify(launch)
        flash("Launch deleted successfully!", "success")
        return redirect(url_for("mission_control.list_launches"))
