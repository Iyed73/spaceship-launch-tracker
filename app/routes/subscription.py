from app.blueprints import subscription_bp as bp
from app.views.subscription.subscribe import SubscribeView
from app.views.subscription.confirm import ConfirmView


bp.add_url_rule("/subscribe",
                view_func=SubscribeView.as_view("subscribe"))

bp.add_url_rule("/confirm/<token>",
                view_func=ConfirmView.as_view("confirm"))
