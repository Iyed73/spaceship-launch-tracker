from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from flask import flash, redirect, url_for
from flask.typing import ResponseReturnValue
from flask_login import current_user, login_required

# Same shape Flask uses for View.decorators: a decorator returns a view of the same type
F = TypeVar("F", bound=Callable[..., ResponseReturnValue])


def logged_out_required(func: F) -> F:
    @wraps(func)
    def decorated_function(*args: Any, **kwargs: Any) -> ResponseReturnValue:
        if current_user.is_authenticated:
            return redirect(url_for("main.index"))
        return func(*args, **kwargs)

    return cast(F, decorated_function)


def admin_required(func: F) -> F:
    @wraps(func)
    @login_required
    def decorated_function(*args: Any, **kwargs: Any) -> ResponseReturnValue:
        if current_user.role != "admin":
            flash("You don't have permission to access this page.", "warning")
            return redirect(url_for("main.index"))
        return func(*args, **kwargs)

    return cast(F, decorated_function)


def spectator_required(func: F) -> F:
    @wraps(func)
    @login_required
    def decorated_function(*args: Any, **kwargs: Any) -> ResponseReturnValue:
        if current_user.role != "spectator":
            flash("You don't have permission to access this page.", "warning")
            return redirect(url_for("main.index"))
        return func(*args, **kwargs)

    return cast(F, decorated_function)
