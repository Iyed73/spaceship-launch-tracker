from app.models import Spaceship
from urllib.parse import urlparse


def test_create_spaceship_success(app, login_admin):
    data = {"name": "test spaceship", "height": 1, "mass": 1, "payload_capacity": 1, "thrust_at_liftoff": 1}
    response = login_admin.post("/spaceship/create", data=data, follow_redirects=True)
    assert response.status_code == 200
    final_url = urlparse(response.request.url).path
    assert final_url == "/spaceship"
    with app.app_context():
        assert Spaceship.query.count() == 1
        assert Spaceship.query.first().name == "test spaceship"


def test_create_spaceship_fails_unauthorized(app, login_user):
    data = {"name": "test spaceship", "height": 1, "mass": 1, "payload_capacity": 1, "thrust_at_liftoff": 1}
    login_user.post("/spaceship/create", data=data)
    with app.app_context():
        assert Spaceship.query.count() == 0
