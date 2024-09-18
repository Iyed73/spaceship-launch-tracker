from app.tasks.event_categories import EventCategory
from app import mail
from flask import render_template
from app.models import Subscriber
from rq.job import Retry
from flask_mail import Message
from flask import current_app


def process_subscribers_event(event, **kwargs):
    from app import app
    with app.app_context():
        subscribers = Subscriber.query.all()
        for subscriber in subscribers:
            print(subscriber)
            if subscriber.is_confirmed:
                current_app.task_queue.enqueue(notify_subscriber, subscriber, event, **kwargs, retry=Retry(max=3))


def notify_subscriber(subscriber, event, **kwargs):
    from app import app
    with app.app_context():
        match event:
            case EventCategory.NEW_LAUNCH:
                launch = kwargs["launch"]
                html = render_template("subscription/new_launch_email.html", receiver=subscriber.name, launch=launch)
                subject = f"New Launch: {launch.mission} at {launch.launch_site.name}"
            case EventCategory.LAUNCH_UPDATE:
                launch = kwargs["launch"]
                html = render_template("subscription/update_launch_email.html", receiver=subscriber.name, launch=launch)
                subject = f"Launch Update: {launch.mission}"
            case EventCategory.REMINDER:
                launch = kwargs["launch"]
                html = render_template("subscription/reminder_email.html", receiver=subscriber.name, launch=launch)
                subject = f"Launch Happening soon: {launch.mission}"
            case EventCategory.LAUNCH_DELETE:
                launch = kwargs["launch"]
                html = render_template("subscription/cancel_launch_email.html", receiver=subscriber.name, launch=launch)
                subject = f"Launch canceled: {launch.mission}"
        message = Message(recipients=[subscriber.email], sender=current_app.config["APP_EMAIL"])
        message.html = html
        message.subject = subject
        mail.send(message)
