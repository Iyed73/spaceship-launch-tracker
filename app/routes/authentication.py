from app.blueprints import authentication_bp as bp
from app.views.authentication.register import RegisterView
from app.views.authentication.login import LoginView
from app.views.authentication.logout import LogoutView
from app.views.authentication.confirm import ConfirmView


bp.add_url_rule("/register",
                view_func=RegisterView.as_view("register"))

bp.add_url_rule("/login",
                view_func=LoginView.as_view("login"))

bp.add_url_rule("/logout",
                view_func=LogoutView.as_view("logout"))

bp.add_url_rule("/confirm/<token>",
                view_func=ConfirmView.as_view("confirm"))
