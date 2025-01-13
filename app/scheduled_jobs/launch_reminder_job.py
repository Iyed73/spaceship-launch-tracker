from datetime import datetime, timedelta
from app.models import Launch, LaunchReminder
from app import db, scheduler
from config import Config


LOCK_NAME = "lock:remind_subscribers"


@scheduler.task('interval', id='remind_subscribers', seconds=Config.SUBSCRIBERS_REMINDER_JOB_INTERVAL)
def remind_subscribers():
    app = scheduler.app

    with app.app_context():
        lock = app.redis.lock(LOCK_NAME, timeout=Config.SUBSCRIBERS_REMINDER_JOB_LOCK_TIMEOUT)
        if not lock.acquire(blocking=False):
            return

        try:
            now = datetime.now()
            launches = Launch.get_upcoming_with_no_reminders(now, timedelta(seconds=Config.LAUNCH_REMINDER_WINDOW))

            for launch in launches:
                if LaunchReminder.claim(launch.id):
                    app.task_queue.enqueue(f"app.tasks.launch_reminder.process_launch_reminder_notification", launch_id=launch.id)
                db.session.commit()
        finally:
            lock.release()
