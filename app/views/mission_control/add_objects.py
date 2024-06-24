from flask.views import MethodView
from flask import render_template, flash, url_for, redirect
from flask_login import current_user
from app.models import Spaceship, LaunchSite, Launch
from app.forms import SpaceshipForm, LaunchSiteForm, LaunchForm
from app import db
from abc import ABC, abstractmethod
from app.decorators import admin_required


class BaseAddView(MethodView, ABC):
    decorators = [admin_required]

    def __init__(self, object_type, form, redirect_url):
        self.object_type = object_type
        self.form = form
        self.redirect_url = redirect_url

    @abstractmethod
    def create_instance(self):
        pass

    def get(self):
        if not current_user.is_authenticated:
            return redirect(url_for("main.index"))
        return render_template("mission_control/add_object.html", title="Add " + self.object_type, form=self.form)

    def post(self):
        if self.form.validate_on_submit() and current_user.is_authenticated:
            obj = self.create_instance()
            self.form.populate_obj(obj)
            obj.creator_id = current_user.id
            db.session.add(obj)
            db.session.commit()
            flash(self.object_type + " added successfully!", "success")
            return redirect(self.redirect_url)
        return render_template("mission_control/add_object.html", title="Add " + self.object_type, form=self.form)


class AddSpaceshipView(BaseAddView):
    def __init__(self):
        form = SpaceshipForm()
        super().__init__("Spaceship", form, url_for("mission_control.list_spaceships"))

    def create_instance(self):
        return Spaceship()


class AddLaunchSiteView(BaseAddView):
    def __init__(self):
        form = LaunchSiteForm()
        super().__init__("LaunchSite", form, url_for("mission_control.list_launchsites"))

    def create_instance(self):
        return LaunchSite()


class AddLaunchView(BaseAddView):
    def __init__(self):
        form = LaunchForm()
        super().__init__("Launch", form, url_for("mission_control.list_launches"))
        self.form.spaceship_id.choices = [(spaceship.id, spaceship.name) for spaceship in Spaceship.query.all()]
        self.form.launch_site_id.choices = [(site.id, site.name) for site in LaunchSite.query.all()]

    def create_instance(self):
        return Launch()
