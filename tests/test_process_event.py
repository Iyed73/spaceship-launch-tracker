from app.tasks.event_categories import EventCategory
from app.tasks.process_event import process_subscribers_event, notify_subscriber


def test_process_subscribers_event_only_confirmed_subscribers(mocker, app, subscribers, mocked_queue):
    with app.app_context():
        mocker.patch("app.app", new=app)
    process_subscribers_event(EventCategory.NEW_LAUNCH, launch="doesn't matter")
    assert mocked_queue.call_count == 1


def test_notify_subscriber_new_launch_event(mocker, app, subscribers, launch):
    with app.app_context():
        mock_send_mail = mocker.patch("app.mail.send")

    notify_subscriber(subscribers[0], EventCategory.NEW_LAUNCH, launch=launch)

    assert mock_send_mail.call_count == 1
    message = mock_send_mail.call_args[0][0]
    assert message.subject == "New Launch: mission at launch site"
    assert subscribers[0].email in message.recipients
