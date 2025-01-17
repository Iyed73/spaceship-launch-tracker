from urllib.parse import urlsplit

from flask import flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue
from flask.views import MethodView
from flask_login import login_user
from sqlalchemy import select

from app import db, limiter
from app.decorators import logged_out_required
from app.forms import LoginForm
from app.models import User


class LoginView(MethodView):
    decorators = [logged_out_required]

    def __init__(self) -> None:
        self.form = LoginForm()

    def get(self) -> ResponseReturnValue:
        return render_template("authentication/login.html", title="login", form=self.form)

    @limiter.limit("10 per minute")
    def post(self) -> ResponseReturnValue:
        if self.form.validate_on_submit():
            user = db.session.scalar(select(User).where(User.username == self.form.username.data))
            if user is None:
                flash("Invalid username", "danger")
                return redirect(url_for("authentication.login"))
            if not user.check_password(self.form.password.data):
                flash("Invalid password", "danger")
                return redirect(url_for("authentication.login"))
            login_user(user, remember=self.form.remember_me.data)
            next_page = request.args.get("next")
            if not next_page or urlsplit(next_page).netloc != "":
                next_page = url_for("main.index")
            return redirect(next_page)
        return render_template("authentication/login.html", title="login", form=self.form)
