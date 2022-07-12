import pytest

from main.schemas.category import CategorySchema
from tests.data import CATEGORY_INFOS
from tests.schemas.common import load_invalid_data_and_assert


class Data:
    SAMPLE_NAME = CATEGORY_INFOS[0]["name"]

    EDGE_CASE_VALID_NAMES = ["a", "a" * 80]

    INVALID_NAMES = [1, "", "a" * 81]  # Not a string  # Empty len 0  # Too long


@pytest.mark.parametrize("valid_name", [Data.SAMPLE_NAME] + Data.EDGE_CASE_VALID_NAMES)
def test_category_schema_name_valid(valid_name):
    valid_data = {
        "name": valid_name,
    }
    category = CategorySchema().load(valid_data)
    assert category["name"] == valid_data["name"]


@pytest.mark.parametrize("invalid_name", Data.INVALID_NAMES)
def test_category_schema_name_invalid(invalid_name):
    invalid_data = {
        "name": invalid_name,
    }
    load_invalid_data_and_assert(CategorySchema, invalid_data)
