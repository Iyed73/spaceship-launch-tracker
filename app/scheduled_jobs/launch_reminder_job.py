from datetime import datetime, timedelta
from app.models import Launch, LaunchReminder
from app import db, scheduler


@scheduler.task('interval', id='remind_subscribers', minutes=30)
def remind_subscribers():
    from launchvault import app

    with app.app_context():
        now = datetime.now()
        launches = Launch.get_upcoming_with_no_reminders(now, timedelta(hours=2))

        for launch in launches:
            app.task_queue.enqueue(f"app.tasks.launch_reminder.process_launch_reminder_notification", launch=launch)
            reminder = LaunchReminder(launch=launch)
            db.session.add(reminder)
            db.session.commit()
