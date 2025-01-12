from app.models import UserReminder, LaunchReminder
from app import db
from urllib.parse import urlparse


def test_set_reminder_success(app, login_user, user, upcoming_launch):
    response = login_user.post(f"/launches/{upcoming_launch.id}/reminder", follow_redirects=True)
    assert response.status_code == 200
    final_url = urlparse(response.request.url).path
    assert final_url == "/launches"
    assert b"Reminder Set" in response.data
    with app.app_context():
        assert UserReminder.query.count() == 1
        reminder = UserReminder.query.first()
        assert reminder.user_id == user.id
        assert reminder.launch_id == upcoming_launch.id


def test_set_reminder_redirects_to_next_page(login_user, upcoming_launch):
    response = login_user.post(f"/launches/{upcoming_launch.id}/reminder?next=/launches/mine")
    assert response.status_code == 302
    assert response.location == "/launches/mine"


def test_set_reminder_ignores_external_next_page(login_user, upcoming_launch):
    response = login_user.post(f"/launches/{upcoming_launch.id}/reminder?next=https://example.com")
    assert response.location == "/launches"


def test_remove_reminder_success(app, login_user, upcoming_launch):
    login_user.post(f"/launches/{upcoming_launch.id}/reminder")
    response = login_user.post(f"/launches/{upcoming_launch.id}/reminder", follow_redirects=True)
    assert b"Reminder removed for mission." in response.data
    with app.app_context():
        assert UserReminder.query.count() == 0


def test_set_reminder_fails_past_launch(app, login_user, launch):
    response = login_user.post(f"/launches/{launch.id}/reminder", follow_redirects=True)
    assert b"Reminders can only be set for upcoming launches." in response.data
    with app.app_context():
        assert UserReminder.query.count() == 0


def test_set_reminder_fails_already_sent(app, login_user, upcoming_launch):
    with app.app_context():
        db.session.add(LaunchReminder(launch_id=upcoming_launch.id))
        db.session.commit()

    response = login_user.post(f"/launches/{upcoming_launch.id}/reminder", follow_redirects=True)
    assert b"Reminders for mission have already been sent." in response.data
    with app.app_context():
        assert UserReminder.query.count() == 0


def test_set_reminder_not_found(login_user):
    response = login_user.post("/launches/00000000-0000-0000-0000-000000000000/reminder")
    assert response.status_code == 404


def test_set_reminder_fails_logged_out(app, client, upcoming_launch):
    response = client.post(f"/launches/{upcoming_launch.id}/reminder")
    assert response.status_code == 302
    assert urlparse(response.location).path == "/authentication/login"
    with app.app_context():
        assert UserReminder.query.count() == 0


def test_set_reminder_fails_admin(app, login_admin, upcoming_launch):
    response = login_admin.post(f"/launches/{upcoming_launch.id}/reminder", follow_redirects=True)
    assert b"You don&#39;t have permission to access this page." in response.data
    with app.app_context():
        assert UserReminder.query.count() == 0


def test_set_reminder_warns_unconfirmed_user(login_user, upcoming_launch):
    response = login_user.post(f"/launches/{upcoming_launch.id}/reminder", follow_redirects=True)
    assert b"confirm your email to receive it." in response.data


def test_upcoming_launches_reminder_button(client, upcoming_launch):
    response = client.get("/launches")
    assert b"Set Reminder" in response.data
    assert b"/authentication/login?next=" in response.data


def test_upcoming_launches_no_reminder_button_for_admin(login_admin, upcoming_launch):
    response = login_admin.get("/launches")
    assert b"Set Reminder" not in response.data


def test_my_launches(login_user, upcoming_launch):
    response = login_user.get("/launches/mine")
    assert response.status_code == 200
    assert b"<title>My Launches</title>" in response.data
    assert b"No upcoming launches found." in response.data

    login_user.post(f"/launches/{upcoming_launch.id}/reminder")
    response = login_user.get("/launches/mine")
    assert b"mission" in response.data
    assert b"Reminder Set" in response.data


def test_my_launches_fails_admin(login_admin):
    response = login_admin.get("/launches/mine", follow_redirects=True)
    final_url = urlparse(response.request.url).path
    assert final_url == "/home"
