from app.blueprints import mission_control_bp as bp
from app.views.mission_control.create_spaceship import CreateSpaceshipView
from app.views.mission_control.create_launchsite import CreateLaunchSiteView
from app.views.mission_control.create_launch import CreateLaunchView
from app.views.mission_control.update_launch import UpdateLaunchView
from app.views.mission_control.update_launchsite import UpdateLaunchSiteView
from app.views.mission_control.update_spaceship import UpdateSpaceshipView
from app.views.mission_control.list_items import ListSpaceshipsView, ListLaunchSitesView, ListLaunchesView
from app.views.mission_control.delete_spaceship import DeleteSpaceshipView
from app.views.mission_control.delete_launch import DeleteLaunchView
from app.views.mission_control.delete_launchsite import DeleteLaunchSiteView
from app.views.mission_control.panel import MissionControlView

bp.add_url_rule("/panel",
                   view_func=MissionControlView.as_view("panel"))

bp.add_url_rule("/spaceship/create",
                   view_func=CreateSpaceshipView.as_view("create_spaceship"))

bp.add_url_rule("/spaceship",
                   view_func=ListSpaceshipsView.as_view("list_spaceships"))

bp.add_url_rule("/spaceship/<int:id>",
                   view_func=UpdateSpaceshipView.as_view("update_spaceship"))

bp.add_url_rule("/spaceship/<int:id>/delete",
                   view_func=DeleteSpaceshipView.as_view("delete_spaceship"))

bp.add_url_rule("/launchsite/create",
                   view_func=CreateLaunchSiteView.as_view("create_launchsite"))

bp.add_url_rule("/launchsite",
                   view_func=ListLaunchSitesView.as_view("list_launchsites"))

bp.add_url_rule("/launchsite/<int:id>",
                   view_func=UpdateLaunchSiteView.as_view("update_launchsite"))

bp.add_url_rule("/launchsite/<int:id>/delete",
                   view_func=DeleteLaunchSiteView.as_view("delete_launchsite"))

bp.add_url_rule("/launch/create",
                   view_func=CreateLaunchView.as_view("create_launch"))

bp.add_url_rule("/launch",
                   view_func=ListLaunchesView.as_view("list_launches"))

bp.add_url_rule("/launch/<uuid:id>",
                   view_func=UpdateLaunchView.as_view("update_launch"))

bp.add_url_rule("/launch/<uuid:id>/delete",
                   view_func=DeleteLaunchView.as_view("delete_launch"))
