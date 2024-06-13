from flask.views import MethodView
from flask import render_template, flash, url_for, redirect, request
from flask_login import current_user
from app.models import User
from app.forms import RegistrationForm
from app import db, limiter


class RegisterView(MethodView):
    def __init__(self):
        self.form = RegistrationForm()

    def get(self):
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        return render_template('register.html', title='Register', form=self.form)

    @limiter.limit("10 per minute")
    def post(self):
        if self.form.validate_on_submit():
            user = User(username=self.form.username.data,
                        email=self.form.email.data)
            user.set_password(self.form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('authentication.login'))
        return render_template('register.html', title='Register', form=self.form)

