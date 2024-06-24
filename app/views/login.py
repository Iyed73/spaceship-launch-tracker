from flask.views import MethodView
from flask import render_template, flash, url_for, redirect, request
from flask_login import login_user, current_user
from app.models import User
from app.forms import LoginForm
from app import db, limiter
from sqlalchemy import select
from urllib.parse import urlsplit


class LoginView(MethodView):
    def __init__(self):
        self.form = LoginForm()

    def get(self):
        if current_user.is_authenticated:
            return redirect(url_for("main.index"))
        return render_template("login.html", title="login", form=self.form)

    @limiter.limit("10 per minute")
    def post(self):
        if self.form.validate_on_submit():
            user = db.session.scalar(
                select(User).where(User.username == self.form.username.data)
            )
            if user is None:
                flash("Invalid username","danger")
                return redirect(url_for("authentication.login"))
            if not user.check_password(self.form.password.data):
                flash("Invalid password","danger")
                return redirect(url_for("authentication.login"))
            login_user(user, remember=self.form.remember_me.data)
            next_page = request.args.get("next")
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for("main.index")
            return redirect(next_page)
        return render_template("login.html", title="login", form=self.form)
