from tests.data import USER_INFOS


class Data:
    DATA_WITH_EXISTED_EMAIL = USER_INFOS[0]
    DATA_WITH_NEW_EMAIL = {"email": "test@email.com", "password": "A valid password 1"}
    DATA_WITH_INVALID_PASSWORD = {
        "email": "test2@email.com",
        "password": "not a valid one",
    }


def test_post_request_email_valid(client):
    response = client.post("/users", json=Data.DATA_WITH_NEW_EMAIL)
    assert response.status_code == 200
    assert response.json == {}


def test_post_request_email_invalid(client):
    response = client.post("/users", json=Data.DATA_WITH_EXISTED_EMAIL)
    assert response.status_code == 400
    assert response.json["error_code"] == 400001


def test_post_request_password_invalid(client):
    response = client.post("/users", json=Data.DATA_WITH_INVALID_PASSWORD)
    assert response.status_code == 400
    assert response.json["error_code"] == 400001
