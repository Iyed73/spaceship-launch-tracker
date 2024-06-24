from flask.views import View
from flask import render_template, url_for
from app.models import Spaceship, LaunchSite, Launch
from flask_wtf.csrf import generate_csrf
from abc import ABC, abstractmethod
from app.decorators import admin_required


class BaseListView(View, ABC):
    decorators = [admin_required]

    def __init__(self, title, object_type, columns, create_url):
        self.title = title
        self.object_type = object_type
        self.columns = columns
        self.create_url = create_url

    @abstractmethod
    def get_objects(self):
        pass

    @abstractmethod
    def get_update_url(self, object_id):
        pass

    @abstractmethod
    def get_delete_url(self, object_id):
        pass

    def dispatch_request(self):
        return render_template("mission_control/list_objects.html",
                               title=self.title,
                               create_url=self.create_url,
                               object_type=self.object_type,
                               columns=self.columns,
                               objects=self.get_objects(),
                               update_url=self.get_update_url,
                               delete_url=self.get_delete_url,
                               csrf=generate_csrf())


class ListSpaceshipsView(BaseListView):
    def __init__(self):
        super().__init__(
                        title="Spaceships",
                        object_type="Spaceship",
                        columns=["Name", "Description", "Height", "Mass", "Payload Capacity", "Thrust at Liftoff"],
                        create_url=url_for("mission_control.add_spaceship"))

    def get_objects(self):
        return Spaceship.query.all()

    def get_update_url(self, object_id):
        return url_for("mission_control.update_spaceship", id=object_id)

    def get_delete_url(self, object_id):
        return url_for("mission_control.delete_spaceship", id=object_id)


class ListLaunchSitesView(BaseListView):
    def __init__(self):
        super().__init__(
                        title="Launch Sites",
                        object_type="Launch Site",
                        columns=["Name", "Location"],
                        create_url=url_for("mission_control.add_launchsite"))

    def get_objects(self):
        return LaunchSite.query.all()

    def get_update_url(self, object_id):
        return url_for("mission_control.update_launchsite", id=object_id)

    def get_delete_url(self, object_id):
        return url_for("mission_control.delete_launchsite", id=object_id)


class ListLaunchesView(BaseListView):
    def __init__(self):
        super().__init__(
                        title="Launches",
                        object_type="Launch",
                        columns=["Mission", "Description", "Launch Timestamp", "Spaceship", "Launch Site"],
                        create_url=url_for("mission_control.add_launch"))

    def get_objects(self):
        return Launch.query.all()

    def get_update_url(self, object_id):
        return url_for("mission_control.update_launch", id=object_id)

    def get_delete_url(self, object_id):
        return url_for("mission_control.delete_launch", id=object_id)
