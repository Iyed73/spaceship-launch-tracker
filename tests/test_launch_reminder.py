# from app.scheduled_jobs.launch_reminder_job import remind_subscribers
# from app import db
# from app.models import LaunchEvent
# from app.tasks.event_categories import EventCategory
#
#
# def test_remind_subscribers_no_upcoming_launches(app, mocker, mocked_queue):
#     mocker.patch("app.app", new=app)
#     remind_subscribers()
#     assert mocked_queue.call_count == 0
#
#
# def test_remind_subscribers_with_upcoming_launch(app, mocker, launch_after_2_hours, mocked_queue):
#     mocker.patch("app.app", new=app)
#     mocker.patch('app.db.session.add')
#     mocker.patch('app.db.session.commit')
#     remind_subscribers()
#     assert mocked_queue.call_count == 1
#
#
# def test_remind_subscribers_upcoming_launch_with_reminder(mocker, app, launch_after_2_hours, mocked_queue):
#     mocker.patch("app.app", new=app)
#     launch_event = LaunchEvent(id="something", name="existing reminder", launch=launch_after_2_hours, category=EventCategory.REMINDER)
#     with app.app_context():
#         db.session.add(launch_event)
#         db.session.commit()
#
#     remind_subscribers()
#
#     assert mocked_queue.call_count == 0
#
#
#
