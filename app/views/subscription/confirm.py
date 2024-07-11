from flask.views import View
from flask import flash, url_for, redirect
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from app.models import Subscriber
from app import db
from sqlalchemy import select


class ConfirmView(View):
    EXPIRATION = 3600

    def dispatch_request(self, token):
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            data = serializer.loads(
                token, salt=current_app.config["SECURITY_PASSWORD_SALT"], max_age=self.EXPIRATION
            )
            subscriber = db.session.scalar(
                select(Subscriber).where(Subscriber.email == data)
            )
            if subscriber is None or subscriber.is_confirmed:
                raise Exception
            subscriber.is_confirmed = True
            db.session.add(subscriber)
            db.session.commit()
            flash("You have confirmed your account. Thanks!", "success")
        except:
            flash("The confirmation link is invalid or expired", "danger")
        return redirect(url_for("main.index"))
