import pytest
from app.models import Subscriber
from app import db


def test_subscribe_success(client, app):
    response = client.post("/subscription/subscribe",
                           data={"email": "test@test.com", "name": "test"})
    assert response.status_code == 302
    with app.app_context():
        assert Subscriber.query.count() == 1
        assert Subscriber.query.first().email == "test@test.com"


def test_subscribe_fails_invalid_form(client, app):
    response = client.post("/subscription/subscribe",
                           data={"email": "tes.com", "name": "tes"})
    assert b"Invalid email address." in response.data
    assert b"Field must be between 4 and 64 characters long." in response.data


def test_subscribe_fails_email_used(client, app, mocker):
    subscriber = Subscriber(email="test@test.com", name="test")
    with app.app_context():
        db.session.add(subscriber)
        db.session.commit()

    mocker.patch("app.views.authentication.register.db.session.add")
    mocker.patch("app.views.authentication.register.db.session.commit")

    response = client.post("/authentication/register",
                           data={"email": "test@test.com", "name": "test"})

    assert response.status_code == 200
    assert not db.session.add.called
    assert not db.session.commit.called
