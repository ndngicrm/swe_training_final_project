from main.resources.token import TokenResource
from tests.data import USER_INFOS


class Data:
    VALID_CREDENTIAL = USER_INFOS[0]
    INVALID_CREDENTIAL = {"email": "somewrong@email.com", "password": "dasdas"}


def test_token_resource_credential_valid(client):
    response = client.post("/access-tokens", json=Data.VALID_CREDENTIAL)
    assert response.status_code == 200
    assert "access_token" in response.json
    assert 1 == TokenResource.get_id_from_token(
        "Bearer " + response.json["access_token"]
    )


def test_token_resource_credential_invalid(client):
    response = client.post("/access-tokens", json=Data.INVALID_CREDENTIAL)
    assert response.status_code == 401


def test_need_user_token_decorator(client):
    response = client.post("/categories", json={})
    assert response.status_code == 400
