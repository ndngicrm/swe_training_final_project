import pytest

from main.resources.token import TokenResource
from tests.data import CATEGORY_INFOS


class Data:
    TOKEN_FOR_USER_ID_1 = "Bearer " + TokenResource.get_token(1)

    GET_VALID_PARAMS = [
        dict(),
        dict(page=10),
        dict(per_page=50),
        dict(page=1, per_page=1),
    ]

    GET_INVALID_PARAMS = [
        dict(page=0),  # Less than 1
        dict(per_page=0),  # Less than 1
        dict(per_page=51),  # Max exceeded
    ]

    POST_VALID_REQUETS = [dict(name="Category 1"), dict(name="a" * 80)]

    POST_INVALID_REQUESTS = [
        dict(name=CATEGORY_INFOS[0]["name"]),  # Existed
        dict(name=""),  # Empty, represent validation error
    ]

    DELETE_VALID_REQUEST = dict(
        category_id=1,
        token="Bearer " + TokenResource.get_token(CATEGORY_INFOS[0]["user_id"]),
    )

    DELETE_INVALID_REQUEST = [
        dict(  # Valid token, but no category existed
            category_id=1000,
            token="Bearer " + TokenResource.get_token(CATEGORY_INFOS[0]["user_id"]),
        ),
        dict(  # Valid token, but no permission
            category_id=1,
            token="Bearer " + TokenResource.get_token(CATEGORY_INFOS[9]["user_id"]),
        ),
    ]


@pytest.mark.parametrize("valid_param", Data.GET_VALID_PARAMS)
def test_category_resource_get_params_valid_no_auth(client, valid_param):
    response = client.get("/categories", query_string=valid_param)
    assert response.status_code == 200
    for i in ["total_items", "per_page", "page"]:
        assert i in response.json
    if response.json["categories"]:
        for category in response.json["categories"]:
            for i in ["id", "name", "is_owner"]:
                assert i in category
            assert not category["is_owner"]


def test_category_resource_get_params_valid_with_auth(client):
    response = client.get(
        "/categories", headers={"Authorization": Data.TOKEN_FOR_USER_ID_1}
    )
    assert response.status_code == 200
    assert response.json["categories"][0]["is_owner"]


@pytest.mark.parametrize("valid_request", Data.POST_VALID_REQUETS)
def test_category_resource_post_request_valid(client, valid_request):
    response = client.post(
        "/categories",
        json=valid_request,
        headers={"Authorization": Data.TOKEN_FOR_USER_ID_1},
    )
    assert response.status_code == 200
    for i in ["id", "name", "is_owner"]:
        assert i in response.json


@pytest.mark.parametrize("invalid_request", Data.POST_INVALID_REQUESTS)
def test_category_resource_post_request_invalid(client, invalid_request):
    response = client.post(
        "/categories",
        json=invalid_request,
        headers={"Authorization": Data.TOKEN_FOR_USER_ID_1},
    )
    assert response.status_code == 400


def test_category_resource_delete_request_valid(client):
    response = client.delete(
        f"/categories/{Data.DELETE_VALID_REQUEST['category_id']}",
        headers={"Authorization": Data.DELETE_VALID_REQUEST["token"]},
    )
    assert response.status_code == 200


def test_category_resource_delete_request_invalid_not_found(client):
    response = client.delete(
        f"/categories/{Data.DELETE_INVALID_REQUEST[0]['category_id']}",
        headers={"Authorization": Data.DELETE_INVALID_REQUEST[0]["token"]},
    )
    assert response.status_code == 404


def test_category_resource_delete_request_invalid_forbidden(client):
    response = client.delete(
        f"/categories/{Data.DELETE_INVALID_REQUEST[1]['category_id']}",
        headers={"Authorization": Data.DELETE_INVALID_REQUEST[1]["token"]},
    )
    assert response.status_code == 403
