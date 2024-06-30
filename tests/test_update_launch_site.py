from app.models import LaunchSite
from app import db


def test_update_launch_site_success(app, login_admin):
    with app.app_context():
        launch_site = LaunchSite(name="test launch site", location="somewhere")
        db.session.add(launch_site)
        db.session.commit()
        db.session.refresh(launch_site)
    data = {"name": "updated launch site", "location": "somewhere else"}
    response = login_admin.post(f"/launchsite/{launch_site.id}", data=data, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        updated_launch_site = LaunchSite.query.get(launch_site.id)
        assert updated_launch_site.name == "updated launch site"
        assert updated_launch_site.location == "somewhere else"


def test_update_launch_site_not_found(app, login_admin):
    data = {"name": "updated launch site", "location": "somewhere else"}
    response = login_admin.post("/launchsite/9", data=data, follow_redirects=True)
    assert response.status_code == 404
