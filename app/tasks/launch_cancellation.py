from app import db
from flask import render_template, current_app
from app.models import Subscriber, Launch
from rq.job import Retry
from app.tasks.send_email_notification import send_email_notification
from config import Config


def process_launch_cancellation_notification(launch_id):
    launch = db.session.get(Launch, launch_id)
    subscribers = Subscriber.query.filter_by(is_confirmed=True).all()

    for subscriber in subscribers:
        html = render_template("subscription/cancel_launch_email.html", receiver=subscriber.name, launch=launch)
        subject = f"Launch canceled: {launch.mission}"
        current_app.task_queue.enqueue(send_email_notification,
                                       recipient=subscriber.email,
                                       content=html,
                                       subject=subject,
                                       retry=Retry(max=Config.TASK_QUEUE_MAX_RETRIES))

