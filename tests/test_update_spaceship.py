from app.models import Spaceship
from app import db


def test_update_spaceship_success(app, login_admin):
    with app.app_context():
        spaceship = Spaceship(name="test spaceship", height=1, mass=1, payload_capacity=1, thrust_at_liftoff=1)
        db.session.add(spaceship)
        db.session.commit()
        db.session.refresh(spaceship)
    data = {"name": "updated spaceship", "height": 2, "mass": 2, "payload_capacity": 2, "thrust_at_liftoff": 2}
    response = login_admin.post(f"/spaceship/{spaceship.id}", data=data, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        updated_spaceship = Spaceship.query.get(spaceship.id)
        assert updated_spaceship.name == "updated spaceship"
        assert updated_spaceship.height == 2
        assert updated_spaceship.mass == 2
        assert updated_spaceship.payload_capacity == 2
        assert updated_spaceship.thrust_at_liftoff == 2


def test_spaceship_site_not_found(app, login_admin):
    data = {"name": "updated spaceship", "height": 2, "mass": 2, "payload_capacity": 2, "thrust_at_liftoff": 2}
    response = login_admin.post("/spaceship/9", data=data, follow_redirects=True)
    assert response.status_code == 404
