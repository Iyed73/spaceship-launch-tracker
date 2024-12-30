from app.models import Launch, LaunchEvent


def test_create_launch_records_event(mocker, app, login_admin, admin, launch):
    mocker.patch("app.views.mission_control.create_launch.CreateLaunchView.notify")

    data = {"mission": "test mission", "launch_timestamp": "2024-06-27T11:57", "spaceship_id": launch.spaceship_id,
            "launch_site_id": launch.launch_site_id}
    login_admin.post("/launch/create", data=data)
    with app.app_context():
        assert LaunchEvent.query.count() == 1
        event = LaunchEvent.query.first()
        assert event.creator_id == admin.id
        assert event.changes == {"mission": [None, "test mission"],
                                 "launch_timestamp": [None, "2024-06-27T11:57:00"],
                                 "spaceship_id": [None, launch.spaceship_id],
                                 "launch_site_id": [None, launch.launch_site_id],
                                 "status": [None, "scheduled"]}


def test_update_launch_records_event(mocker, app, login_admin, launch, launch_data):
    mocker.patch("app.views.mission_control.update_launch.UpdateLaunchView.notify")

    data = {**launch_data, "launch_timestamp": "2024-06-28T10:37", "status": "delayed"}
    login_admin.post(f"/launch/{launch.id}", data=data)
    with app.app_context():
        events = Launch.query.get(launch.id).events
        assert len(events) == 1
        assert events[0].changes == {"launch_timestamp": ["2024-06-27T11:57:00", "2024-06-28T10:37:00"],
                                     "status": ["scheduled", "delayed"]}


def test_update_launch_without_changes_records_no_event(mocker, app, login_admin, launch, launch_data):
    notify = mocker.patch("app.views.mission_control.update_launch.UpdateLaunchView.notify")

    login_admin.post(f"/launch/{launch.id}", data=launch_data)
    with app.app_context():
        assert LaunchEvent.query.count() == 0
    assert not notify.called


def test_cancel_launch_records_event(app, login_admin, launch, mocked_queue):
    login_admin.post(f"/launch/{launch.id}/delete")
    with app.app_context():
        assert LaunchEvent.query.first().changes == {"status": ["scheduled", "cancelled"]}


def test_launch_history(mocker, login_admin, launch, launch_data):
    mocker.patch("app.views.mission_control.update_launch.UpdateLaunchView.notify")

    login_admin.post(f"/launch/{launch.id}", data={**launch_data, "status": "delayed"})
    response = login_admin.get(f"/launch/{launch.id}/history")
    assert response.status_code == 200
    assert b"scheduled &rarr; delayed" in response.data
