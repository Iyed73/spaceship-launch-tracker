from flask.views import MethodView
from flask import render_template, flash, redirect, url_for
from app import db
from app.models import LaunchSite, Spaceship, Launch
from app.forms import LaunchSiteForm, SpaceshipForm, LaunchForm
from app.decorators import admin_required


class BaseUpdateView(MethodView):
    decorators = [admin_required]

    def __init__(self, object_type, form, redirect_url):
        self.object_type = object_type
        self.form = form
        self.redirect_url = redirect_url

    def get_item_or_404(self, id):
        pass

    def get(self, id):
        item = self.get_item_or_404(id)
        self.form.process(obj=item)
        return render_template("mission_control/update_object.html", title="Update " + self.object_type, form=self.form)

    def post(self, id):
        item = self.get_item_or_404(id)
        if self.form.validate_on_submit():
            self.form.populate_obj(item)
            db.session.commit()
            flash(self.object_type + " updated successfully!", "success")
            return redirect(url_for(self.redirect_url))
        return render_template("mission_control/update_object.html", title="Update " + self.object_type, form=self.form)


class UpdateSpaceshipView(BaseUpdateView):
    def __init__(self):
        form = SpaceshipForm()
        super().__init__("Spaceship", form, "mission_control.list_spaceships")

    def get_item_or_404(self, id):
        item = Spaceship.query.get_or_404(id)
        return item


class UpdateLaunchSiteView(BaseUpdateView):
    def __init__(self):
        form = LaunchSiteForm()
        super().__init__("Launch Site", form, "mission_control.list_launchsites")

    def get_item_or_404(self, id):
        item = LaunchSite.query.get_or_404(id)
        return item


class UpdateLaunchView(BaseUpdateView):
    def __init__(self):
        form = LaunchForm()
        super().__init__("Launch", form, "mission_control.list_launches")
        self.form.spaceship_id.choices = [(spaceship.id, spaceship.name) for spaceship in Spaceship.query.all()]
        self.form.launch_site_id.choices = [(site.id, site.name) for site in LaunchSite.query.all()]

    def get_item_or_404(self, id):
        item = Launch.query.get_or_404(id)
        return item
