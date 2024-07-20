from flask import redirect, url_for, flash
from flask.views import MethodView
from app.models import Launch, LaunchEvent
from app import db
from flask import current_app
from app.decorators import admin_required
from app.tasks.process_event import process_subscribers_event
from app.tasks.event_categories import EventCategory


class DeleteLaunchView(MethodView):
    decorators = [admin_required]

    @staticmethod
    def create_event(launch):
        job = current_app.task_queue.enqueue(process_subscribers_event, EventCategory.LAUNCH_DELETE, launch=launch)
        event = LaunchEvent(id=job.get_id(), name=f"delete launch: {launch.mission}", launch=launch, category=EventCategory.LAUNCH_DELETE)
        db.session.add(event)
        db.session.commit()

    def post(self, id):
        launch = Launch.query.get_or_404(id)
        db.session.delete(launch)
        db.session.commit()
        self.create_event(launch)
        flash("Launch deleted successfully!", "success")
        return redirect(url_for("mission_control.list_launches"))
