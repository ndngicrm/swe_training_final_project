# This test is to fill in the missing case of coverage report
from sqlalchemy.exc import SQLAlchemyError

from main.commons.decorators import secure_sql_error
from main.models.base import QueryMixin
from main.resources.user import UserResource


def test_filter_by_allow_attributes_decorator_none():
    class TmpModel(QueryMixin):
        filter_allowed = []

    assert not TmpModel.find_by_attributes(name="A")


def test_routing_not_found(client):
    response = client.get("/some-random_routes")
    assert response.status_code == 404


def test_internal_server_error(mocker, client):
    mocker.patch.object(UserResource, "post", side_effect=Exception)
    response = client.post("/users")
    assert response.status_code == 500


def test_sql_error(mocker):
    @secure_sql_error
    def raise_sql_error():
        raise SQLAlchemyError

    try:
        raise_sql_error()
    except Exception as error:
        assert "SQL Error" in error.error_message
    else:
        assert False
