from flask.views import View
from flask_login import logout_user
from flask import url_for, redirect


class LogoutView(View):
    def dispatch_request(self):
        logout_user()
        return redirect(url_for('main.index'))

