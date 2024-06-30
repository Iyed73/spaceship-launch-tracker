from flask.views import View
from flask import render_template, url_for
from app.models import Spaceship, LaunchSite, Launch
from flask_wtf.csrf import generate_csrf
from app.decorators import admin_required


class BaseListView(View):
    decorators = [admin_required]

    columns = []

    def __init__(self, model_class, model_name, title, create_reverse_url, update_reverse_url, delete_reverse_url):
        self.model_class = model_class
        self.model_name = model_name
        self.title = title
        self.create_reverse_url = create_reverse_url
        self.update_reverse_url = update_reverse_url
        self.delete_reverse_url = delete_reverse_url

    def get_objects(self):
        return self.model_class.query.all()

    def get_create_url(self):
        return url_for(self.create_reverse_url)

    def get_update_url(self, object_id):
        return url_for(self.update_reverse_url, id=object_id)

    def get_delete_url(self, object_id):
        url_for(self.delete_reverse_url, id=object_id)

    def dispatch_request(self):
        return render_template("mission_control/list_objects.html",
                               title=self.title,
                               model_name=self.model_name,
                               create_url=self.get_create_url(),
                               columns=self.columns,
                               objects=self.get_objects(),
                               update_url=self.get_update_url,
                               delete_url=self.get_delete_url,
                               csrf=generate_csrf())


class ListSpaceshipsView(BaseListView):
    columns=["Name", "Description", "Height", "Mass", "Payload Capacity", "Thrust at Liftoff"]

    def __init__(self):
        super().__init__(
            model_class=Spaceship,
            model_name="Spaceship",
            title="Spaceships",
            create_reverse_url="mission_control.create_spaceship",
            update_reverse_url="mission_control.update_spaceship",
            delete_reverse_url="mission_control.delete_spaceship"
        )


class ListLaunchSitesView(BaseListView):
    columns = ["Name", "Location"]

    def __init__(self):
        super().__init__(
            model_class=LaunchSite,
            model_name="Launch Site",
            title="Launch Sites",
            create_reverse_url="mission_control.create_launchsite",
            update_reverse_url="mission_control.update_launchsite",
            delete_reverse_url="mission_control.delete_launchsite"
        )


class ListLaunchesView(BaseListView):
    columns = ["Mission", "Description", "Launch Timestamp", "Spaceship", "Launch Site"]

    def __init__(self):
        super().__init__(
            model_class=Launch,
            model_name="Launch",
            title="Launches",
            create_reverse_url="mission_control.create_launch",
            update_reverse_url="mission_control.update_launch",
            delete_reverse_url="mission_control.delete_launch"
        )
