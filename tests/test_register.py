from app.models import User
from app import db


def test_register_success(client, app):
    response = client.post("/authentication/register",
                           data={"email": "test@test.com",
                                 "username": "username",
                                 "password": "password",
                                 "password_confirmation": "password"})
    assert response.status_code == 302
    with app.app_context():
        assert User.query.count() == 1
        assert User.query.first().email == "test@test.com"


def test_register_fails_invalid_form(client, app):
    response = client.post("/authentication/register",
                           data={"email": "invalid",
                                 "password": "short",
                                 "password_confirmation": "s"})
    assert b'Invalid email address.' in response.data
    assert b'This field is required.' in response.data
    assert b'Field must be equal to password.' in response.data


def test_register_fails_duplicate_user(client, app, mocker):
    user = User(username="testuser", email="test@test.com")
    user.set_password('password')
    with app.app_context():
        db.session.add(user)
        db.session.commit()

    mocker.patch('app.views.register.db.session.add')
    mocker.patch('app.views.register.db.session.commit')

    response = client.post("/authentication/register",
                           data={"email": "test@test.com",
                                 "username": "testuser",
                                 "password": "password",
                                 "password_confirmation": "password"})

    assert response.status_code == 200
    assert not db.session.add.called
    assert not db.session.commit.called
