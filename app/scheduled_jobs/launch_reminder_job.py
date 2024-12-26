from datetime import datetime, timedelta
from app.models import Launch, LaunchReminder
from app import db, scheduler
from config import Config



@scheduler.task('interval', id='remind_subscribers', seconds=Config.SUBSCRIBERS_REMINDER_JOB_INTERVAL)
def remind_subscribers():
    from launchvault import app

    with app.app_context():
        now = datetime.now()
        launches = Launch.get_upcoming_with_no_reminders(now, timedelta(seconds=Config.LAUNCH_REMINDER_WINDOW))

        for launch in launches:
            app.task_queue.enqueue(f"app.tasks.launch_reminder.process_launch_reminder_notification", launch=launch)
            reminder = LaunchReminder(launch=launch)
            db.session.add(reminder)
            db.session.commit()
