from app.models import Spaceship, Launch, LaunchSite
from app import db
from urllib.parse import urlparse


def setup_launch_data(app):
    with app.app_context():
        spaceship = Spaceship(name="test spaceship", height=1, mass=1, payload_capacity=1, thrust_at_liftoff=1)
        launch_site = LaunchSite(name="test launch site", location="somewhere")
        db.session.add(launch_site)
        db.session.add(spaceship)
        db.session.commit()
        db.session.refresh(spaceship)
        db.session.refresh(launch_site)
        return spaceship, launch_site


def test_create_launch_success(app, login_admin):
    spaceship, launch_site = setup_launch_data(app)
    data = {"mission": "test mission", "launch_timestamp": "2024-06-27T11:57", "spaceship_id": spaceship.id,
            "launch_site_id": launch_site.id}
    response = login_admin.post("/launch/create", data=data, follow_redirects=True)
    assert response.status_code == 200
    final_url = urlparse(response.request.url).path
    assert final_url == "/launch"
    with app.app_context():
        assert Launch.query.count() == 1
        assert Launch.query.first().mission == "test mission"


def test_create_launch_fails_unauthorized(app, login_user):
    spaceship, launch_site = setup_launch_data(app)
    data = {"mission": "test mission", "launch_timestamp": "2024-06-27T11:57", "spaceship_id": spaceship.id,
            "launch_site_id": launch_site.id}
    login_user.post("/launch/create", data=data, follow_redirects=True)
    with app.app_context():
        assert Launch.query.count() == 0
