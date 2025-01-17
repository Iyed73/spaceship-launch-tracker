from typing import Any

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import create_app, db
from app.models import Launch, LaunchSite, Spaceship, User
from config import DevelopmentConfig

app = create_app(DevelopmentConfig)


@app.shell_context_processor
def make_shell_context() -> dict[str, Any]:
    return {
        "so": so,
        "sa": sa,
        "db": db,
        "User": User,
        "LaunchSite": LaunchSite,
        "Spaceship": Spaceship,
        "Launch": Launch,
    }
