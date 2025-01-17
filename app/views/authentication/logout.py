from flask import redirect, url_for
from flask.typing import ResponseReturnValue
from flask.views import View
from flask_login import logout_user


class LogoutView(View):
    def dispatch_request(self) -> ResponseReturnValue:
        logout_user()
        return redirect(url_for("main.index"))
