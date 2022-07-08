from main.models.user import UserModel
from main.resources.user import UserTokenResource
from tests.data import items_info, users_info


def test_user_resource(client):
    # POST
    # Regular case
    json_request = {"email": "valid1@gmail.com", "password": "ValidPassword1"}
    response = client.post("/users", json=json_request)
    assert response.status_code == 200
    assert response.text == ""

    # Validation error
    json_request = {"email": "invalidemail", "password": "invalidpassword"}
    response = client.post("/users", json=json_request)
    assert response.status_code == 400
    assert response.json["error_code"] == 400001
    keys = response.json["error_data"].keys()
    assert "email" in keys and "password" in keys

    # User in database
    user = UserModel.find_by_email("valid1@gmail.com")
    if user:
        assert True
    else:
        assert False


def test_user_token_resource(client):
    # POST
    # Regular case
    json_request = {"email": users_info[0][0], "password": users_info[0][1]}
    response = client.post("/users/tokens", json=json_request)
    assert response.status_code == 200
    assert response.json["access_token"]

    access_token = response.json["access_token"]

    # Get and decode token
    user1_info = users_info[0]
    token = UserTokenResource.get_token(1)
    user1 = UserTokenResource.get_identity_from_token(token)
    assert user1.email == user1_info[0]

    # Use token
    reponse = client.post(
        "/categories",
        json={"name": "New category"},
        headers={"Authorization": "JWT " + access_token},
    )
    assert reponse.status_code == 200

    # Require user token
    response = client.post("/categories", json={})
    assert response.status_code == 400

    # More test for invalid token needed


def test_category_resource(client):
    # GET
    # Regular cases
    response = client.get("/categories")
    assert response.status_code == 200
    assert response.json["categories"]
    keys = response.json["categories"][0].keys()
    assert "name" in keys
    assert "id" in keys
    assert response.json["page"] == 1
    assert response.json["per_page"] == 20
    assert response.json["total_items"] != 0

    # Invalid params
    response = client.get("/categories", query_string={"per_page": 51})
    assert response.status_code == 400

    response = client.get("/categories", query_string={"a": 1})
    assert response.status_code == 400

    # ACCESS_TOKEN
    access_token = client.post(
        "/users/tokens", json={"email": users_info[0][0], "password": users_info[0][1]}
    ).json["access_token"]

    wrong_access_token = client.post(
        "/users/tokens", json={"email": users_info[1][0], "password": users_info[1][1]}
    ).json["access_token"]

    # POST
    # Regular cases
    json_request = {"name": "New category 1"}
    response = client.post(
        "/categories",
        json=json_request,
        headers={"Authorization": "JWT " + access_token},
    )
    assert response.status_code == 200
    assert "id" in response.json

    id = response.json["id"]

    # DELETE
    # Not owner
    response = client.delete(
        f"categories/{id}", headers={"Authorization": "JWT " + wrong_access_token}
    )
    assert response.status_code == 403

    # Regular cases
    response = client.delete(
        f"/categories/{id}", headers={"Authorization": "JWT " + access_token}
    )
    assert response.status_code == 200
    assert response.text == ""

    # Not found
    response = client.delete(
        "/categories/1000", headers={"Authorization": "JWT " + access_token}
    )
    assert response.status_code == 404

    # Add case delete all


def test_item_resource(client):
    # GET
    # Regular cases
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json["items"]
    keys = response.json["items"][0].keys()
    assert "name" in keys
    assert "id" in keys
    assert response.json["page"] == 1
    assert response.json["per_page"] == 20
    assert response.json["total_items"] != 0

    # Regular cases with category id
    response = client.get("/items", query_string={"category_id": 1})
    for item in response.json["items"]:
        assert item["category_id"] == 1

    # Invalid params
    response = client.get("/items", query_string={"per_page": 51})
    assert response.status_code == 400

    response = client.get("/items", query_string={"a": 1})
    assert response.status_code == 400

    # GET with ID
    # Regular cases
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json["name"] == items_info[0][0]

    # Not found
    response = client.get("/items/10000")
    assert response.status_code == 404

    # ACCESS_TOKEN
    access_token = client.post(
        "/users/tokens", json={"email": users_info[0][0], "password": users_info[0][1]}
    ).json["access_token"]

    wrong_access_token = client.post(
        "/users/tokens", json={"email": users_info[1][0], "password": users_info[1][1]}
    ).json["access_token"]

    # POST
    # Regular cases
    json_request = {"name": "New item 1", "description": "Ahdsansa", "category_id": 1}
    response = client.post(
        "/items",
        json=json_request,
        headers={"Authorization": "JWT " + access_token},
    )
    assert response.status_code == 200
    assert "id" in response.json

    # Category not found
    json_request = {"name": "New item 2", "description": "Ahdsansa", "category_id": 500}
    response = client.post(
        "/items", json=json_request, headers={"Authorization": "JWT " + access_token}
    )
    assert response.status_code == 404

    # No permission
    json_request = {"name": "New item 2", "description": "Ahdsansa", "category_id": 9}
    response = client.post(
        "/items", json=json_request, headers={"Authorization": "JWT " + access_token}
    )
    assert response.status_code == 403

    # PUT
    # Regular cases
    json_request = {"name": "New item 3", "description": "alkdjas", "category_id": 1}
    response = client.put(
        "/items/1", json=json_request, headers={"Authorization": "JWT" + access_token}
    )

    # Item not found
    json_request = {"name": "New item 4", "description": "kjas", "category_id": 1}
    response = client.put(
        "/items/1000",
        json=json_request,
        headers={"Authorization": "JWT " + access_token},
    )
    assert response.status_code == 404

    # No permission
    response = client.put(
        "/items/1",
        json=json_request,
        headers={"Authorization": "JWT " + wrong_access_token},
    )
    assert response.status_code == 403

    # DELETE
    # Regular cases
    response = client.delete(
        "/items/1", headers={"Authorization": "JWT " + access_token}
    )
    assert response.status_code == 200

    # Item not found
    response = client.delete(
        "/items/10000", headers={"Authorization": "JWT " + access_token}
    )

    # No permission
    response = client.delete(
        "/items/3", headers={"Authorization": "JWT " + wrong_access_token}
    )
    assert response.status_code == 403
