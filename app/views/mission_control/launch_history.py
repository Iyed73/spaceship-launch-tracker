from flask.views import View
from flask import render_template
from app.models import Launch
from app.decorators import admin_required


class LaunchHistoryView(View):
    decorators = [admin_required]

    def dispatch_request(self, id):
        launch = Launch.query.get_or_404(id)
        return render_template("mission_control/launch_history.html", launch=launch)
