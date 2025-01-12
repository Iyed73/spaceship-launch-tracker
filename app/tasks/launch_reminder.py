from app import create_app, db
from flask import render_template
from app.models import Subscriber, Launch, User, UserReminder
from rq.job import Retry
from config import DevelopmentConfig
from app.tasks.send_email_notification import send_email_notification
from config import Config


app = create_app(DevelopmentConfig)
app.app_context().push()


def process_launch_reminder_notification(launch_id):
    launch = db.session.get(Launch, launch_id)
    subscribers = Subscriber.query.filter_by(is_confirmed=True).all()
    users = User.query.join(UserReminder).filter(UserReminder.launch_id == launch_id, User.is_confirmed).all()

    recipients = {user.email: user.username for user in users}
    recipients.update({subscriber.email: subscriber.name for subscriber in subscribers})

    for email, name in recipients.items():
        html = render_template("subscription/reminder_email.html", receiver=name, launch=launch)
        subject = f"Launch reminder: {launch.mission} at {launch.launch_site.name}"
        app.task_queue.enqueue(send_email_notification,
                               recipient=email,
                               content=html,
                               subject=subject,
                               retry=Retry(max=Config.TASK_QUEUE_MAX_RETRIES))

