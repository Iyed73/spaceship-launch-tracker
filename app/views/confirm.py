from flask.views import View
from flask import  flash, url_for, redirect
from flask_login import login_required, current_user


class ConfirmView(View):
    decorators = [login_required]

    def dispatch_request(self, token):
        if current_user.is_confirmed:
            return redirect(url_for("main.index"))
        if current_user.confirm_token(token):
            flash("You have confirmed your account. Thanks!", "success")
        else:
            flash("The confirmation link is invalid or expired", "danger")
        return redirect(url_for("main.index"))
