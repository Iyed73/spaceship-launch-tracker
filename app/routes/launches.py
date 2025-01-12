from app.blueprints import launches_bp as bp
from app.views.launches.upcoming_launches import UpcomingLaunchesView
from app.views.launches.past_launches import PastLaunchesView
from app.views.launches.my_launches import MyLaunchesView
from app.views.launches.toggle_reminder import ToggleReminderView


bp.add_url_rule("/launches",
                view_func=UpcomingLaunchesView.as_view("upcoming_launches"))

bp.add_url_rule("/launches/past",
                view_func=PastLaunchesView.as_view("past_launches"))

bp.add_url_rule("/launches/mine",
                view_func=MyLaunchesView.as_view("my_launches"))

bp.add_url_rule("/launches/<uuid:id>/reminder",
                view_func=ToggleReminderView.as_view("toggle_reminder"))
