from flask import render_template
from flask.typing import ResponseReturnValue
from flask.views import View

from app.decorators import admin_required
from app.models import Launch, LaunchSite, Spaceship


class MissionControlView(View):
    decorators = [admin_required]

    def dispatch_request(self) -> ResponseReturnValue:
        launch_count = Launch.query.count()
        launchsite_count = LaunchSite.query.count()
        spaceship_count = Spaceship.query.count()
        return render_template(
            "mission_control/panel.html",
            launch_count=launch_count,
            launchsite_count=launchsite_count,
            spaceship_count=spaceship_count,
        )
