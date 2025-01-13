import pytest
from redis.exceptions import ConnectionError
from app.scheduled_jobs.launch_reminder_job import remind_subscribers, LOCK_NAME
from app.models import LaunchReminder
from app import db


def test_remind_subscribers_no_upcoming_launches(app, upcoming_launch, mocked_queue):
    remind_subscribers()
    assert not mocked_queue.called
    with app.app_context():
        assert LaunchReminder.query.count() == 0


def test_remind_subscribers_with_upcoming_launch(app, launch_after_1_hour, mocked_queue):
    remind_subscribers()
    assert mocked_queue.call_count == 1
    assert mocked_queue.call_args.kwargs == {"launch_id": launch_after_1_hour.id}
    with app.app_context():
        assert LaunchReminder.query.count() == 1
        assert LaunchReminder.query.first().launch_id == launch_after_1_hour.id


def test_remind_subscribers_queues_reminder_once(app, launch_after_1_hour, mocked_queue):
    remind_subscribers()
    remind_subscribers()
    assert mocked_queue.call_count == 1
    with app.app_context():
        assert LaunchReminder.query.count() == 1


def test_remind_subscribers_skips_launch_claimed_by_another_process(app, mocker, launch_after_1_hour, mocked_queue):
    mocker.patch("app.models.Launch.get_upcoming_with_no_reminders", return_value=[launch_after_1_hour])
    with app.app_context():
        assert LaunchReminder.claim(launch_after_1_hour.id)
        db.session.commit()

    remind_subscribers()
    assert not mocked_queue.called
    with app.app_context():
        assert LaunchReminder.query.count() == 1


def test_remind_subscribers_skips_when_locked(app, launch_after_1_hour, mocked_queue):
    lock = app.redis.lock(LOCK_NAME, timeout=60)
    assert lock.acquire(blocking=False)
    try:
        remind_subscribers()
    finally:
        lock.release()
    assert not mocked_queue.called
    with app.app_context():
        assert LaunchReminder.query.count() == 0


def test_remind_subscribers_queue_unavailable(app, launch_after_1_hour, mocked_queue):
    mocked_queue.side_effect = ConnectionError
    with pytest.raises(ConnectionError):
        remind_subscribers()
    with app.app_context():
        assert LaunchReminder.query.count() == 0

    mocked_queue.side_effect = None
    remind_subscribers()
    assert mocked_queue.call_count == 2
    with app.app_context():
        assert LaunchReminder.query.count() == 1
