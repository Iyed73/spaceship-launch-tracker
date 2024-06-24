from functools import wraps
from flask_login import current_user, fresh_login_required
from flask import flash, url_for, redirect


def logged_out_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("main.index"))
        return func(*args, **kwargs)
    return decorated_function


def admin_required(func):
    @wraps(func)
    @fresh_login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != "admin":
            flash("You don't have permission to access this page.", "warning")
            return redirect(url_for("main.index"))
        return func(*args, **kwargs)
    return decorated_function
