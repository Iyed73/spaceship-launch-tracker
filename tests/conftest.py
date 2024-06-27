import pytest
from app import create_app, db
from config import TestingConfig
from app.models import User


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
