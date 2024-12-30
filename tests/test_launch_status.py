import pytest
from app.models import Launch, LaunchStatus


def test_update_launch_status_success(mocker, app, login_admin, launch, launch_data):
    mocker.patch("app.views.mission_control.update_launch.UpdateLaunchView.notify")

    response = login_admin.post(f"/launch/{launch.id}", data={**launch_data, "status": "delayed"},
                                follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert Launch.query.get(launch.id).status == LaunchStatus.DELAYED


def test_update_launch_status_fails_invalid_transition(app, login_admin, launch, launch_data):
    response = login_admin.post(f"/launch/{launch.id}", data={**launch_data, "status": "succeeded"})
    assert b"Not a valid choice." in response.data
    with app.app_context():
        assert Launch.query.get(launch.id).status == LaunchStatus.SCHEDULED


@pytest.mark.parametrize(("status", "next_status"),
                         ((LaunchStatus.SCHEDULED, LaunchStatus.LAUNCHED),
                          (LaunchStatus.DELAYED, LaunchStatus.SCRUBBED),
                          (LaunchStatus.SCRUBBED, LaunchStatus.SCHEDULED),
                          (LaunchStatus.LAUNCHED, LaunchStatus.SUCCEEDED),))
def test_launch_status_transition_success(status, next_status):
    launch = Launch(status=status)
    launch.status = next_status
    assert launch.status == next_status


@pytest.mark.parametrize(("status", "next_status"),
                         ((LaunchStatus.SCHEDULED, LaunchStatus.SUCCEEDED),
                          (LaunchStatus.LAUNCHED, LaunchStatus.SCHEDULED),
                          (LaunchStatus.FAILED, LaunchStatus.SUCCEEDED),
                          (LaunchStatus.CANCELLED, LaunchStatus.SCHEDULED),))
def test_launch_status_transition_fails(status, next_status):
    launch = Launch(status=status)
    with pytest.raises(ValueError):
        launch.status = next_status
    assert launch.status == status
