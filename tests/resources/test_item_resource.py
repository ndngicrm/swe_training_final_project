import pytest

from main.resources.token import TokenResource
from tests.data import CATEGORY_INFOS, ITEM_INFOS


class Data:
    TOKEN_FOR_USER_ID_1 = "Bearer " + TokenResource.get_token(1)

    GET_VALID_PARAMS = [
        dict(),
        dict(category_id=1, page=10),
        dict(per_page=50),
        dict(page=1, per_page=1),
    ]

    GET_INVALID_PARAMS = [
        dict(page=0),  # Less than 1
        dict(per_page=0),  # Less than 1
        dict(per_page=51),  # Max exceeded
    ]

    GET_INVALID_PARAM_CATEGORY_NOT_FOUND = dict(category_id=100)

    POST_VALID_REQUET = dict(
        name="Category 1", description="olhndasnda dsaoidnklas", category_id=1
    )

    POST_INVALID_REQUESTS = [
        dict(
            name=ITEM_INFOS[0]["name"], description="dabksdas", category_id=1
        ),  # Existed
        dict(name=""),  # Empty, represent validation error
    ]

    PUT_VALID_REQUESTS = [
        dict(name=ITEM_INFOS[0]["name"]),  # change name with same name
        dict(name="Some valid name"),  # change name with valid name
        dict(description="Dsadas"),
        dict(category_id=2),  # change to category with permission
    ]

    PUT_INVALID_REQUEST = [
        dict(name=ITEM_INFOS[1]["name"]),  # change to used name
        dict(name="", description=""),  # represent validation error
    ]

    DELETE_VALID_REQUEST = dict(
        item_id=1,
        token=TOKEN_FOR_USER_ID_1,
    )

    DELETE_INVALID_REQUEST = [
        dict(  # Valid token, but no item existed
            item_id=1000, token=TOKEN_FOR_USER_ID_1
        ),
        dict(  # Valid token, but no permission
            item_id=1,
            token="Bearer " + TokenResource.get_token(CATEGORY_INFOS[9]["user_id"]),
        ),
    ]


@pytest.mark.parametrize("valid_param", Data.GET_VALID_PARAMS)
def test_item_resource_get_params_valid_no_auth(client, valid_param):
    response = client.get("/items", query_string=valid_param)
    assert response.status_code == 200
    for i in ["total_items", "per_page", "page"]:
        assert i in response.json
    if response.json["items"]:
        for item in response.json["items"]:
            for i in ["id", "name", "is_owner", "description", "category_id"]:
                assert i in item
            assert not item["is_owner"]


def test_item_resource_get_params_valid_with_auth(client):
    response = client.get("/items", headers={"Authorization": Data.TOKEN_FOR_USER_ID_1})
    assert response.status_code == 200
    assert response.json["items"][0]["is_owner"]


def test_item_resource_get_params_invalid_not_found(client):
    response = client.get(
        "/items", query_string=Data.GET_INVALID_PARAM_CATEGORY_NOT_FOUND
    )
    assert response.status_code == 404


def test_item_resource_get_with_id_valid_no_auth(client):
    response = client.get("/items/1")
    for i in ["id", "name", "is_owner", "description", "category_id"]:
        assert i in response.json
    assert not response.json["is_owner"]


def test_item_resource_get_with_id_valid_with_auth(client):
    response = client.get(
        "/items/1", headers={"Authorization": Data.TOKEN_FOR_USER_ID_1}
    )
    for i in ["id", "name", "is_owner", "description", "category_id"]:
        assert i in response.json
    assert response.json["is_owner"]


def test_item_resource_post_request_valid(client):
    response = client.post(
        "/items",
        json=Data.POST_VALID_REQUET,
        headers={"Authorization": Data.TOKEN_FOR_USER_ID_1},
    )
    assert response.status_code == 200
    for i in ["id", "name", "is_owner", "description", "category_id"]:
        assert i in response.json


@pytest.mark.parametrize("invalid_request", Data.POST_INVALID_REQUESTS)
def test_item_resource_post_request_invalid(client, invalid_request):
    response = client.post(
        "/items",
        json=invalid_request,
        headers={"Authorization": Data.TOKEN_FOR_USER_ID_1},
    )
    assert response.status_code == 400


@pytest.mark.parametrize("valid_request", Data.PUT_VALID_REQUESTS)
def test_item_resource_put_request_valid(client, valid_request):
    response = client.put(
        f"/items/{1}",
        json=valid_request,
        headers={"Authorization": Data.TOKEN_FOR_USER_ID_1},
    )
    assert response.status_code == 200
    for i in ["id", "name", "is_owner", "description", "category_id"]:
        assert i in response.json


@pytest.mark.parametrize("invalid_request", Data.PUT_INVALID_REQUEST)
def test_item_resource_put_request_invalid(client, invalid_request):
    response = client.put(
        f"/items/{1}",
        json=invalid_request,
        headers={"Authorization": Data.TOKEN_FOR_USER_ID_1},
    )
    assert response.status_code == 400


def test_item_resource_delete_request_valid(client):
    response = client.delete(
        f"/items/{Data.DELETE_VALID_REQUEST['item_id']}",
        headers={"Authorization": Data.DELETE_VALID_REQUEST["token"]},
    )
    assert response.status_code == 200


def test_category_resource_delete_request_invalid_not_found(client):
    response = client.delete(
        f"/items/{Data.DELETE_INVALID_REQUEST[0]['item_id']}",
        headers={"Authorization": Data.DELETE_INVALID_REQUEST[0]["token"]},
    )
    assert response.status_code == 404


def test_category_resource_delete_request_invalid_forbidden(client):
    response = client.delete(
        f"/items/{Data.DELETE_INVALID_REQUEST[1]['item_id']}",
        headers={"Authorization": Data.DELETE_INVALID_REQUEST[1]["token"]},
    )
    assert response.status_code == 403
