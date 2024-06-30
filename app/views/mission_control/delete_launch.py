from flask import redirect, url_for, flash
from flask.views import MethodView
from app.models import Launch
from app import db
from app.decorators import admin_required


class DeleteLaunchView(MethodView):
    decorators = [admin_required]

    def post(self, id):
        obj = Launch.query.get_or_404(id)
        db.session.delete(obj)
        db.session.commit()
        flash("Launch deleted successfully!", "success")
        return redirect(url_for("mission_control.list_launch"))
