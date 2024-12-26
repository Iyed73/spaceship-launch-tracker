from app import create_app
from flask import render_template
from app.models import Subscriber
from rq.job import Retry
from config import DevelopmentConfig
from app.tasks.send_email_notification import send_email_notification
from config import Config


app = create_app(DevelopmentConfig)
app.app_context().push()


def process_launch_creation_notification(launch):
    subscribers = Subscriber.query.filter_by(is_confirmed=True).all()

    for subscriber in subscribers:
        html = render_template("subscription/new_launch_email.html", receiver=subscriber.name, launch=launch)
        subject = f"New Launch: {launch.mission} at {launch.launch_site.name}"
        app.task_queue.enqueue(send_email_notification,
                               recipient=subscriber.email,
                               content=html,
                               subject=subject,
                               retry=Retry(max=Config.TASK_QUEUE_MAX_RETRIES))

