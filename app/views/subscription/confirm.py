from flask import current_app, flash, redirect, url_for
from flask.typing import ResponseReturnValue
from flask.views import View
from itsdangerous import BadData, URLSafeTimedSerializer
from sqlalchemy import select

from app import db
from app.models import Subscriber


class ConfirmView(View):
    EXPIRATION = 3600

    def dispatch_request(self, token: str) -> ResponseReturnValue:
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            email = serializer.loads(token, salt=current_app.config["SECURITY_PASSWORD_SALT"], max_age=self.EXPIRATION)
        except BadData:
            email = None
        subscriber = db.session.scalar(select(Subscriber).where(Subscriber.email == email)) if email else None
        if subscriber is None or subscriber.is_confirmed:
            flash("The confirmation link is invalid or expired", "danger")
            return redirect(url_for("main.index"))
        subscriber.is_confirmed = True
        db.session.add(subscriber)
        db.session.commit()
        flash("You have confirmed your account. Thanks!", "success")
        return redirect(url_for("main.index"))
