from flask import current_app, flash, redirect, render_template, url_for
from flask.typing import ResponseReturnValue
from flask.views import MethodView
from flask_mail import Message

from app import db, limiter
from app.decorators import logged_out_required
from app.email import send_email
from app.forms import RegistrationForm
from app.models import User


class RegisterView(MethodView):
    decorators = [logged_out_required]

    def __init__(self) -> None:
        self.form = RegistrationForm()

    @staticmethod
    def send_confirmation_email(user: User) -> bool:
        token = user.generate_confirmation_token()
        confirm_url = url_for("authentication.confirm", token=token, _external=True)
        message = Message(recipients=[user.email], sender=current_app.config["APP_EMAIL"])
        html = render_template("authentication/confirm.html", confirm_url=confirm_url)
        subject = "Confirm Your Account"
        message.html = html
        message.subject = subject
        return send_email(message)

    def get(self) -> ResponseReturnValue:
        return render_template("authentication/register.html", title="Register", form=self.form)

    @limiter.limit("10 per minute")
    def post(self) -> ResponseReturnValue:
        if self.form.validate_on_submit():
            user = User(username=self.form.username.data, email=self.form.email.data)
            user.set_password(self.form.password.data)
            db.session.add(user)
            db.session.flush()
            if not self.send_confirmation_email(user):
                db.session.rollback()
                flash("An error occurred, please try again later.", "danger")
                return render_template("authentication/register.html", title="Register", form=self.form)
            db.session.commit()
            flash("Congratulations, you are now a registered user!", "success")
            flash("A confirmation email has been sent to you by email.", "success")
            return redirect(url_for("authentication.login"))
        return render_template("authentication/register.html", title="Register", form=self.form)
