import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app, db
from app.models import User, LaunchSite, Spaceship, Launch
from config import DevelopmentConfig


app = create_app(DevelopmentConfig)


@app.shell_context_processor
def make_shell_context():
    return {'so': so, 'sa': sa, 'db': db, 'User': User, 'LaunchSite': LaunchSite
            , 'Spaceship': Spaceship, 'Launch': Launch}


