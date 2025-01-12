from redis.exceptions import ConnectionError
from app.models import Launch, LaunchStatus
from app import db
from urllib.parse import urlparse


def test_cancel_launch_success(app, login_admin, launch, mocked_queue):
    response = login_admin.post(f"/launch/{launch.id}/delete", follow_redirects=True)
    assert response.status_code == 200
    final_url = urlparse(response.request.url).path
    assert final_url == "/launch"
    with app.app_context():
        assert Launch.query.count() == 1
        assert Launch.query.first().status == LaunchStatus.CANCELLED
    assert mocked_queue.call_args.kwargs == {"launch_id": launch.id}


def test_cancel_launch_fails_already_launched(app, login_admin, launch, mocked_queue):
    with app.app_context():
        Launch.query.get(launch.id).status = LaunchStatus.LAUNCHED
        db.session.commit()

    response = login_admin.post(f"/launch/{launch.id}/delete", follow_redirects=True)
    assert b"A launched launch cannot be cancelled." in response.data
    with app.app_context():
        assert Launch.query.first().status == LaunchStatus.LAUNCHED
    assert not mocked_queue.called


def test_cancel_launch_fails_unauthorized(app, login_user, launch):
    login_user.post(f"/launch/{launch.id}/delete", follow_redirects=True)
    with app.app_context():
        assert Launch.query.first().status == LaunchStatus.SCHEDULED


def test_cancel_launch_success_queue_unavailable(app, login_admin, launch, mocked_queue):
    mocked_queue.side_effect = ConnectionError
    response = login_admin.post(f"/launch/{launch.id}/delete", follow_redirects=True)
    assert response.status_code == 200
    assert b"Subscribers could not be notified about this launch." in response.data
    with app.app_context():
        assert Launch.query.first().status == LaunchStatus.CANCELLED
