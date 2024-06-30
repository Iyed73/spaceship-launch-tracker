from app.models import LaunchSite
from urllib.parse import urlparse


def test_create_launch_site_success(app, login_admin):
    data = {"name": "test launch site", "location": "somewhere"}
    response = login_admin.post("/launchsite/create", data=data, follow_redirects=True)
    assert response.status_code == 200
    final_url = urlparse(response.request.url).path
    assert final_url == "/launchsite"
    with app.app_context():
        assert LaunchSite.query.count() == 1
        assert LaunchSite.query.first().name == "test launch site"


def test_create_launch_site_fails_unauthorized(app, login_user):
    data = {"name": "test launch site", "location": "somewhere"}
    login_user.post("/launchsite/create", data=data)
    with app.app_context():
        assert LaunchSite.query.count() == 0
