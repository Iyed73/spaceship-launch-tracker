import pytest
from app import create_app, db
from config import TestingConfig
from app.models import User, Subscriber, Launch, LaunchSite, Spaceship
from datetime import datetime, timedelta


@pytest.fixture()
def app():
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin(app):
    user = User(username="admin", email="admin@admin.com", role="admin")
    user.set_password("password")
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
    return user


@pytest.fixture()
def login_admin(client, admin):
    with client:
        client.post("/authentication/login", data={
            "username": "admin",
            "password": "password",
        })
        return client
    
    
@pytest.fixture()
def user(app):
    user = User(username="user", email="user@user.com")
    user.set_password("password")
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
    return user


@pytest.fixture()
def login_user(client, user):
    with client:
        client.post("/authentication/login", data={
            "username": "user",
            "password": "password",
        })
        return client


@pytest.fixture()
def subscribers(app):
    subscriber1 = Subscriber(email="test1@test.com", name="Test 1", is_confirmed=True)
    subscriber2 = Subscriber(email="test2@test.com", name="Test 2", is_confirmed=False)
    with app.app_context():
        db.session.add(subscriber1)
        db.session.add(subscriber2)
        db.session.commit()
        db.session.refresh(subscriber1)
        db.session.refresh(subscriber2)
    return [subscriber1, subscriber2]


@pytest.fixture()
def mocked_queue(mocker, app):
    with app.app_context():
        mocked_queue = mocker.patch("app.task_queue.enqueue")
    return mocked_queue

@pytest.fixture()
def launch(app):
    with app.app_context():
        spaceship = Spaceship(name="spaceship", height=1, mass=1, payload_capacity=1, thrust_at_liftoff=1)
        launch_site = LaunchSite(name="launch site", location="somewhere")
        launch = Launch(mission="mission", launch_timestamp="2024-06-27T11:57", spaceship=spaceship,
                        launch_site=launch_site)
        db.session.add(spaceship)
        db.session.add(launch_site)
        db.session.add(launch)
        db.session.commit()
        db.session.refresh(launch)
        db.session.refresh(spaceship)
        db.session.refresh(launch_site)
    return launch


@pytest.fixture()
def launch_after_1_hour(app):
    with app.app_context():
        launch_timestamp = datetime.utcnow() + timedelta(hours=1)
        launch_timestamp = launch_timestamp.strftime("%Y-%m-%dT%H:%M")
        spaceship = Spaceship(name="spaceship", height=1, mass=1, payload_capacity=1, thrust_at_liftoff=1)
        launch_site = LaunchSite(name="launch site", location="somewhere")
        launch = Launch(mission="mission", launch_timestamp=launch_timestamp, spaceship=spaceship,
                        launch_site=launch_site)
        db.session.add(spaceship)
        db.session.add(launch_site)
        db.session.add(launch)
        db.session.commit()
        db.session.refresh(launch)
        db.session.refresh(spaceship)
        db.session.refresh(launch_site)
    return launch


@pytest.fixture()
def mock_send_email_notification(mocker):
    mock_send_email_notification = mocker.patch("app.tasks.launch_update.send_email_notification")
    return mock_send_email_notification

