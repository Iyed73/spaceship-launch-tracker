from flask.views import MethodView
from flask import render_template, flash, url_for, redirect, current_app
from flask_login import current_user
from app.models import Subscriber
from app.forms import SubscriptionForm
from app import db, limiter
from flask_mail import Message
from app import mail
from sqlalchemy import select


class SubscribeView(MethodView):
    def __init__(self):
        self.form = SubscriptionForm()

    @staticmethod
    def send_confirmation_email(subscriber):
        token = subscriber.generate_confirmation_token()
        confirm_url = url_for("subscription.confirm", token=token, _external=True)
        message = Message(recipients=[subscriber.email], sender=current_app.config["APP_EMAIL"])
        html = render_template("subscription/confirm.html", confirm_url=confirm_url)
        subject = "Confirm Your Email"
        message.html = html
        message.subject = subject
        mail.send(message)

    def get(self):
        return render_template("subscription/subscribe.html", title="subscribe", form=self.form)

    @limiter.limit("5 per minute, 20 per hour")
    def post(self):
        if self.form.validate_on_submit():
            subscriber = db.session.scalar(select(Subscriber).where(Subscriber.email == self.form.email.data))
            if subscriber is not None:
                self.send_confirmation_email(subscriber)
                flash("You have already subscribed before, please confirm your email.", "warning")
            else:
                subscriber = Subscriber(email=self.form.email.data, name=self.form.name.data)
                db.session.add(subscriber)
                db.session.commit()
                self.send_confirmation_email(subscriber)
                flash("Please confirm your email to become a subscriber.", "success")
            return redirect(url_for("main.index"))
        return render_template("subscription/subscribe.html", title="subscribe", form=self.form)
