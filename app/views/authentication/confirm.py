from flask import flash, redirect, url_for
from flask.typing import ResponseReturnValue
from flask.views import View
from flask_login import current_user, login_required


class ConfirmView(View):
    decorators = [login_required]

    def dispatch_request(self, token: str) -> ResponseReturnValue:
        if current_user.is_confirmed:
            return redirect(url_for("main.index"))
        if current_user.confirm_token(token):
            flash("You have confirmed your account. Thanks!", "success")
        else:
            flash("The confirmation link is invalid or expired", "danger")
        return redirect(url_for("main.index"))
