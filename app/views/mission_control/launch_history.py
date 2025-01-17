from uuid import UUID

from flask import render_template
from flask.typing import ResponseReturnValue
from flask.views import View

from app.decorators import admin_required
from app.models import Launch


class LaunchHistoryView(View):
    decorators = [admin_required]

    def dispatch_request(self, id: UUID) -> ResponseReturnValue:
        launch = Launch.query.get_or_404(id)
        return render_template("mission_control/launch_history.html", launch=launch)
