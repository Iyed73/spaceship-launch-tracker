from app.models import Spaceship, Launch, LaunchSite
from app import db


def test_update_spaceship(app, login_admin):
    with app.app_context():
        spaceship = Spaceship(name="test spaceship", height=1, mass=1, payload_capacity=1, thrust_at_liftoff=1)
        db.session.add(spaceship)
        db.session.commit()
        db.session.refresh(spaceship)
    data = {"name": "updated spaceship", "height": 2, "mass": 2, "payload_capacity": 2, "thrust_at_liftoff": 2}
    response = login_admin.post(f"/spaceship/update/{spaceship.id}", data=data, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        updated_spaceship = Spaceship.query.get(spaceship.id)
        assert updated_spaceship.name == "updated spaceship"
        assert updated_spaceship.height == 2
        assert updated_spaceship.mass == 2
        assert updated_spaceship.payload_capacity == 2
        assert updated_spaceship.thrust_at_liftoff == 2


def test_update_launch_site(app, login_admin):
    with app.app_context():
        launch_site = LaunchSite(name="test launch site", location="somewhere")
        db.session.add(launch_site)
        db.session.commit()
        db.session.refresh(launch_site)
    data = {"name": "updated launch site", "location": "somewhere else"}
    response = login_admin.post(f"/launchsite/update/{launch_site.id}", data=data, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        updated_launch_site = LaunchSite.query.get(launch_site.id)
        assert updated_launch_site.name == "updated launch site"
        assert updated_launch_site.location == "somewhere else"


def test_update_launch(app, login_admin):
    with app.app_context():
        spaceship1 = Spaceship(name="test spaceship", height=1, mass=1, payload_capacity=1, thrust_at_liftoff=1)
        launch_site1 = LaunchSite(name="test launch site", location="somewhere")
        spaceship2 = Spaceship(name="test spaceship 2", height=1, mass=1, payload_capacity=1, thrust_at_liftoff=1)
        launch_site2 = LaunchSite(name="test launch site 2", location="somewhere")
        launch = Launch(mission="test mission", launch_timestamp="2024-06-27T11:57", spaceship=spaceship1, launch_site=launch_site1)
        db.session.add(spaceship1)
        db.session.add(spaceship2)
        db.session.add(launch_site1)
        db.session.add(launch_site2)
        db.session.add(launch)
        db.session.commit()
        db.session.refresh(launch)
        db.session.refresh(spaceship1)
        db.session.refresh(spaceship2)
        db.session.refresh(launch_site1)
        db.session.refresh(launch_site2)
    data = {"mission": "updated mission", "launch_timestamp": "2024-06-28T10:37", "spaceship_id": spaceship2.id,
            "launch_site_id": launch_site2.id}
    response = login_admin.post(f"/launch/update/{launch.id}", data=data, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        updated_launch = Launch.query.get(launch.id)
        assert updated_launch.mission == "updated mission"
        assert str(updated_launch.launch_timestamp) == "2024-06-28 10:37:00"
        assert updated_launch.spaceship_id == spaceship2.id
        assert updated_launch.launch_site_id == launch_site2.id
