from app.models import Spaceship, Launch, LaunchSite
from app import db


def test_update_launch_success(app, login_admin):
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
    response = login_admin.post(f"/launch/{launch.id}", data=data, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        updated_launch = Launch.query.get(launch.id)
        assert updated_launch.mission == "updated mission"
        assert str(updated_launch.launch_timestamp) == "2024-06-28 10:37:00"
        assert updated_launch.spaceship_id == spaceship2.id
        assert updated_launch.launch_site_id == launch_site2.id


def test_update_launch_not_found(app, login_admin):
    data = {"mission": "updated mission", "launch_timestamp": "2024-06-28T10:37", "spaceship_id": 1, "launch_site_id": 1}
    response = login_admin.post("/launch/9", data=data, follow_redirects=True)
    assert response.status_code == 404
