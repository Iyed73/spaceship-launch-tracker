def test_home(client):
    response = client.get('/home')
    assert response.status_code == 200
    assert b"<title>Home</title>" in response.data


def test_app_testing(app):
    assert app.config["TESTING"] is True
