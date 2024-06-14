from app.blueprints import authentication_bp as bp
from app.views.register import RegisterView
from app.views.login import LoginView
from app.views.logout import LogoutView
from app.views.confirm import ConfirmView


bp.add_url_rule("/register",
                view_func=RegisterView.as_view("register"))

bp.add_url_rule("/log",
                view_func=LoginView.as_view("login"))

bp.add_url_rule("/logout",
                view_func=LogoutView.as_view("logout"))

bp.add_url_rule("/confirm/<token>",
                view_func=ConfirmView.as_view("confirm"))
