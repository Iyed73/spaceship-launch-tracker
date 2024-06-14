import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import User, LaunchSite, Spaceship, Launch


@app.shell_context_processor
def make_shell_context():
    return {'so': so, 'sa': sa, 'db': db, 'User': User, 'LaunchSite': LaunchSite
            , 'Spaceship': Spaceship, 'Launch': Launch}
