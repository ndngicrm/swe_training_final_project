import pytest

from main.schemas.base import PaginationParamSchema, SimpleIdSchema
from main.schemas.item import ItemPaginationParamSchema
from tests.schemas.common import load_invalid_data_and_assert


class Data:
    VALID_PAGINATION_PARAMS = [
        dict(per_page=50, page=1),
        dict(per_page=1),
        dict(page=1),
        dict(),
    ]

    INVALID_PAGINATION_PARAMS = [
        dict(per_page=51),  # Max param exceeded
        dict(per_page=0, page=0),  # Lower than 1
        dict(per_page=0),
        dict(page=0),
    ]


@pytest.mark.parametrize("valid_param", Data.VALID_PAGINATION_PARAMS)
def test_pagination_param_schema_valid_and_exist_start_stop(valid_param):
    param = PaginationParamSchema().load(valid_param)
    excluded = {key: param[key] for key in valid_param if key not in ("start", "stop")}
    assert excluded == valid_param
    assert "start" in param and "stop" in param


@pytest.mark.parametrize("invalid_param", Data.INVALID_PAGINATION_PARAMS)
def test_pagination_param_schema_invalid(invalid_param):
    load_invalid_data_and_assert(ItemPaginationParamSchema, invalid_param)


def test_simple_id_schema_invalid():
    load_invalid_data_and_assert(SimpleIdSchema, dict(id=0))
