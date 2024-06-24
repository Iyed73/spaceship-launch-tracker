import pytest
from app.models import User
from app import db


def test_login_success(client, app):
    user = User(username="testuser", email="test@test.com")
    user.set_password("password")
    with app.app_context():
        db.session.add(user)
        db.session.commit()

    response = client.post("/authentication/login", data={
        "username": "testuser",
        "password": "password",
    })
    assert response.status_code == 302


@pytest.mark.parametrize(("username", "password", "message"),
                         (("someone", "12345678", b"Invalid username"),
                         ("testuser", "11111111", b"Invalid password"),))
def test_login_fails(client, app, username, password, message):
    user = User(username="testuser", email="test@test.com")
    user.set_password("12345678")
    with app.app_context():
        db.session.add(user)
        db.session.commit()

    response = client.post("/authentication/login",
                           data={
                            "username": username,
                            "password": password,
                           }, follow_redirects=True)
    assert message in response.data
