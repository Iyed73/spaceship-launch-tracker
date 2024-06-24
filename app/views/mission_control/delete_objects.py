from flask.views import MethodView
from flask import render_template
from app.decorators import admin_required


class BaseDeleteView(MethodView):
    decorators = [admin_required]

    def post(self, id):
        return render_template("mission_control/delete_object.html")


class DeleteSpaceshipView(BaseDeleteView):
    pass


class DeleteLaunchSiteView(BaseDeleteView):
    pass


class DeleteLaunchView(BaseDeleteView):
    pass
