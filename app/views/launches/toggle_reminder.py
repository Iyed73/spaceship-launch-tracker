from flask import flash, url_for, redirect, request
from flask.views import MethodView
from flask_login import current_user
from datetime import datetime
from app.models import Launch, UserReminder
from app.forms import ReminderForm
from app import db, limiter
from app.decorators import spectator_required
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from urllib.parse import urlsplit


class ToggleReminderView(MethodView):
    decorators = [spectator_required]

    def __init__(self):
        self.form = ReminderForm()

    @limiter.limit("30 per minute")
    def post(self, id):
        launch = Launch.query.get_or_404(id)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("launches.upcoming_launches")
        if not self.form.validate_on_submit():
            flash("Your request could not be processed, please try again.", "danger")
            return redirect(next_page)
        reminder = db.session.scalar(
            select(UserReminder).where(UserReminder.user_id == current_user.id, UserReminder.launch_id == launch.id)
        )
        if reminder is not None:
            db.session.delete(reminder)
            db.session.commit()
            flash(f"Reminder removed for {launch.mission}.", "success")
        elif launch.launch_timestamp <= datetime.now():
            flash("Reminders can only be set for upcoming launches.", "danger")
        elif launch.launch_reminders:
            flash(f"Reminders for {launch.mission} have already been sent.", "warning")
        else:
            try:
                db.session.add(UserReminder(user_id=current_user.id, launch_id=launch.id))
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
            if current_user.is_confirmed:
                flash(f"Reminder set for {launch.mission}.", "success")
            else:
                flash(f"Reminder set for {launch.mission}, confirm your email to receive it.", "warning")
        return redirect(next_page)
