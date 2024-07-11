from itsdangerous import URLSafeTimedSerializer
from app.models import Subscriber
from app import db
from sqlalchemy import select


def test_confirm_email(client, app):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    token = serializer.dumps("test@test.com", salt=app.config["SECURITY_PASSWORD_SALT"])

    subscriber = Subscriber(email="test@test.com", name="test")
    with app.app_context():
        db.session.add(subscriber)
        db.session.commit()

    response = client.get(f"/subscription/confirm/{token}", follow_redirects=True)

    assert response.status_code == 200
    assert b"You have confirmed your account. Thanks!" in response.data

    with app.app_context():
        subscriber = db.session.scalar(select(Subscriber).where(Subscriber.email == "test@test.com"))
        assert subscriber.is_confirmed


def test_confirmation_invalid(client):
    response = client.get("/subscription/confirm/invalid_token", follow_redirects=True)
    assert b"The confirmation link is invalid or expired" in response.data
