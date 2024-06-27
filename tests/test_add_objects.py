from app.models import Spaceship, Launch, LaunchSite
from app import db


def test_add_spaceship(app, login_admin):
    data = {"name": "test spaceship", "height": 1, "mass": 1, "payload_capacity": 1, "thrust_at_liftoff": 1}
    response = login_admin.post("/spaceship/add", data=data, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert Spaceship.query.count() == 1
        assert Spaceship.query.first().name == "test spaceship"


def test_add_launch_site(app, login_admin):
    data = {"name": "test launch site", "location": "somewhere"}
    response = login_admin.post("/launchsite/add", data=data, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert LaunchSite.query.count() == 1
        assert LaunchSite.query.first().name == "test launch site"


def test_add_launch(app, login_admin):
    with app.app_context():
        spaceship = Spaceship(name="test spaceship", height=1, mass=1, payload_capacity=1, thrust_at_liftoff=1)
        launch_site = LaunchSite(name="test launch site", location="somewhere")
        db.session.add(launch_site)
        db.session.add(spaceship)
        db.session.commit()
        db.session.refresh(spaceship)
        db.session.refresh(launch_site)
    data = {"mission": "test mission", "launch_timestamp": "2024-06-27T11:57", "spaceship_id": spaceship.id,
            "launch_site_id": launch_site.id}
    response = login_admin.post("/launch/add", data=data, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert Launch.query.count() == 1
        assert Launch.query.first().mission == "test mission"
