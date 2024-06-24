from app.blueprints import mission_control_bp as bp
from app.views.mission_control.add_objects import AddSpaceshipView, AddLaunchSiteView, AddLaunchView
from app.views.mission_control.list_objects import ListSpaceshipsView, ListLaunchSitesView, ListLaunchesView
from app.views.mission_control.update_objects import UpdateSpaceshipView, UpdateLaunchSiteView, UpdateLaunchView
from app.views.mission_control.delete_objects import DeleteSpaceshipView, DeleteLaunchSiteView, DeleteLaunchView
from app.views.mission_control.panel import MissionControlView

bp.add_url_rule("/panel",
                view_func=MissionControlView.as_view("panel"))

bp.add_url_rule("/spaceship/add",
                view_func=AddSpaceshipView.as_view("add_spaceship"))

bp.add_url_rule("/spaceship/list",
                view_func=ListSpaceshipsView.as_view("list_spaceships"))

bp.add_url_rule("/spaceship/update/<int:id>",
                view_func=UpdateSpaceshipView.as_view("update_spaceship"))

bp.add_url_rule("/spaceship/delete/<int:id>",
                view_func=DeleteSpaceshipView.as_view("delete_spaceship"))

bp.add_url_rule("/launchsite/add",
                view_func=AddLaunchSiteView.as_view("add_launchsite"))

bp.add_url_rule("/launchsite/list",
                view_func=ListLaunchSitesView.as_view("list_launchsites"))

bp.add_url_rule("/launchsite/update/<int:id>",
                view_func=UpdateLaunchSiteView.as_view("update_launchsite"))

bp.add_url_rule("/launchsite/delete/<int:id>",
                view_func=DeleteLaunchSiteView.as_view("delete_launchsite"))

bp.add_url_rule("/launch/add",
                view_func=AddLaunchView.as_view("add_launch"))

bp.add_url_rule("/launch/list",
                view_func=ListLaunchesView.as_view("list_launches"))

bp.add_url_rule("/launch/update/<uuid:id>",
                view_func=UpdateLaunchView.as_view("update_launch"))

bp.add_url_rule("/launch/delete/<uuid:id>",
                view_func=DeleteLaunchView.as_view("delete_launch"))
