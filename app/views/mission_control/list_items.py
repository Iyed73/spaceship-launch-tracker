from uuid import UUID

from flask import render_template, url_for
from flask.typing import ResponseReturnValue
from flask.views import View
from flask_sqlalchemy.model import Model
from flask_wtf.csrf import generate_csrf

from app.decorators import admin_required
from app.models import Launch, LaunchSite, Spaceship


class BaseListView(View):
    decorators = [admin_required]

    columns: list[str] = []

    def __init__(
        self,
        model_class: type[Model],
        model_name: str,
        title: str,
        create_reverse_url: str,
        update_reverse_url: str,
        delete_reverse_url: str,
        history_reverse_url: str | None = None,
    ) -> None:
        self.model_class = model_class
        self.model_name = model_name
        self.title = title
        self.create_reverse_url = create_reverse_url
        self.update_reverse_url = update_reverse_url
        self.delete_reverse_url = delete_reverse_url
        self.history_reverse_url = history_reverse_url

    def get_objects(self) -> list[Model]:
        return self.model_class.query.all()

    def get_create_url(self) -> str:
        return url_for(self.create_reverse_url)

    def get_update_url(self, object_id: int | UUID) -> str:
        return url_for(self.update_reverse_url, id=object_id)

    def get_delete_url(self, object_id: int | UUID) -> str:
        return url_for(self.delete_reverse_url, id=object_id)

    def get_history_url(self, object_id: int | UUID) -> str:
        return url_for(self.history_reverse_url, id=object_id)

    def dispatch_request(self) -> ResponseReturnValue:
        return render_template(
            "mission_control/list_objects.html",
            title=self.title,
            model_name=self.model_name,
            create_url=self.get_create_url(),
            columns=self.columns,
            objects=self.get_objects(),
            update_url=self.get_update_url,
            delete_url=self.get_delete_url,
            history_url=self.get_history_url if self.history_reverse_url else None,
            csrf=generate_csrf(),
        )


class ListSpaceshipsView(BaseListView):
    columns = ["Name", "Description", "Height", "Mass", "Payload Capacity", "Thrust at Liftoff"]

    def __init__(self) -> None:
        super().__init__(
            model_class=Spaceship,
            model_name="Spaceship",
            title="Spaceships",
            create_reverse_url="mission_control.create_spaceship",
            update_reverse_url="mission_control.update_spaceship",
            delete_reverse_url="mission_control.delete_spaceship",
        )


class ListLaunchSitesView(BaseListView):
    columns = ["Name", "Location"]

    def __init__(self) -> None:
        super().__init__(
            model_class=LaunchSite,
            model_name="Launch Site",
            title="Launch Sites",
            create_reverse_url="mission_control.create_launchsite",
            update_reverse_url="mission_control.update_launchsite",
            delete_reverse_url="mission_control.delete_launchsite",
        )


class ListLaunchesView(BaseListView):
    columns = ["Mission", "Description", "Launch Timestamp", "Status", "Spaceship", "Launch Site"]

    def __init__(self) -> None:
        super().__init__(
            model_class=Launch,
            model_name="Launch",
            title="Launches",
            create_reverse_url="mission_control.create_launch",
            update_reverse_url="mission_control.update_launch",
            delete_reverse_url="mission_control.delete_launch",
            history_reverse_url="mission_control.launch_history",
        )
