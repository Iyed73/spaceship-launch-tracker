import pytest
from app.tasks.launch_creation import process_launch_creation_notification
from app.tasks.launch_update import process_launch_update_notification
from app.tasks.launch_cancellation import process_launch_cancellation_notification
from app.tasks.launch_reminder import process_launch_reminder_notification
from app.tasks.send_email_notification import send_email_notification
from app.models import User, UserReminder
from app import db


@pytest.mark.parametrize(("task", "subject"),
                         ((process_launch_creation_notification, "New Launch: mission at launch site"),
                          (process_launch_update_notification, "Launch Update: mission"),
                          (process_launch_cancellation_notification, "Launch canceled: mission")))
def test_launch_notification_queues_email_for_confirmed_subscribers(app, launch, subscribers, mocked_queue, task,
                                                                     subject):
    with app.app_context():
        task(launch.id)
    assert mocked_queue.call_count == 1
    assert mocked_queue.call_args.args == (send_email_notification,)
    assert mocked_queue.call_args.kwargs["recipient"] == "test1@test.com"
    assert mocked_queue.call_args.kwargs["subject"] == subject
    assert "Hello Test 1," in mocked_queue.call_args.kwargs["content"]


def test_launch_reminder_notification_queues_email_for_users_with_reminder(app, launch, subscribers, user,
                                                                            mocked_queue):
    with app.app_context():
        db.session.get(User, user.id).is_confirmed = True
        db.session.add(UserReminder(user_id=user.id, launch_id=launch.id))
        db.session.commit()
        process_launch_reminder_notification(launch.id)
    recipients = {call.kwargs["recipient"] for call in mocked_queue.call_args_list}
    assert recipients == {"test1@test.com", "user@user.com"}


def test_launch_reminder_notification_skips_unconfirmed_user(app, launch, subscribers, user, mocked_queue):
    with app.app_context():
        db.session.add(UserReminder(user_id=user.id, launch_id=launch.id))
        db.session.commit()
        process_launch_reminder_notification(launch.id)
    assert mocked_queue.call_count == 1
    assert mocked_queue.call_args.kwargs["recipient"] == "test1@test.com"


def test_send_email_notification(app, mocker):
    mocked_send = mocker.patch("app.tasks.send_email_notification.mail.send")
    with app.app_context():
        send_email_notification(recipient="test1@test.com", content="<p>content</p>", subject="subject")
    message = mocked_send.call_args.args[0]
    assert message.recipients == ["test1@test.com"]
    assert message.sender == app.config["APP_EMAIL"]
    assert message.html == "<p>content</p>"
    assert message.subject == "subject"
