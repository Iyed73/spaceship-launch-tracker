from app.blueprints import launches_bp as bp
from app.views.launches.upcoming_launches import UpcomingLaunchesView
from app.views.launches.past_launches import PastLaunchesView


bp.add_url_rule("/launches",
                view_func=UpcomingLaunchesView.as_view("upcoming_launches"))

bp.add_url_rule("/launches/past",
                view_func=PastLaunchesView.as_view("past_launches"))