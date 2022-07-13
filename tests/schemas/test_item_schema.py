import pytest

from main.schemas.item import (
    ItemCreateSchema,
    ItemPaginationParamSchema,
    ItemUpdateSchema,
)
from tests.data import ITEM_INFOS
from tests.schemas.common import load_invalid_data_and_assert


class Data:
    SAMPLE_NAME = ITEM_INFOS[0]["name"]
    SAMPLE_DESCRIPTION = ITEM_INFOS[0]["description"]
    SAMPLE_CATEGORY_ID = ITEM_INFOS[0]["category_id"]

    EDGE_CASE_VALID_NAMES_DESCRIPTION = [("a", "a"), ("a" * 80, "a" * 65535)]

    INVALID_NAMES = [1, "", "a" * 81]  # Not a string  # Empty len 0  # Too long

    INVALID_DESCRIPTIONS = [
        1,  # Not a string
        "",  # Empty len 0
        "a" * 65536,  # Too long
    ]

    INVALID_IDS = ["A", 0]  # Not int  # Less than 1


@pytest.mark.parametrize(
    "valid_name,valid_description",
    [(Data.SAMPLE_NAME, Data.SAMPLE_DESCRIPTION)]
    + Data.EDGE_CASE_VALID_NAMES_DESCRIPTION,
)
def test_item_create_schema_name_description_valid(valid_name, valid_description):
    valid_data = {
        "name": valid_name,
        "description": valid_description,
        "category_id": Data.SAMPLE_CATEGORY_ID,
    }

    item = ItemCreateSchema().load(valid_data)
    assert item["name"] == valid_data["name"]
    assert item["description"] == valid_data["description"]
    assert item["category_id"] == valid_data["category_id"]


@pytest.mark.parametrize("invalid_name", Data.INVALID_NAMES)
def test_item_create_schema_name_invalid(invalid_name):
    invalid_data = {
        "name": invalid_name,
        "description": Data.SAMPLE_DESCRIPTION,
        "category_id": Data.SAMPLE_CATEGORY_ID,
    }
    load_invalid_data_and_assert(ItemCreateSchema, invalid_data)


@pytest.mark.parametrize("invalid_description", Data.INVALID_DESCRIPTIONS)
def test_item_create_schema_description_invalid(invalid_description):
    invalid_data = {
        "name": Data.SAMPLE_NAME,
        "description": invalid_description,
        "category_id": Data.SAMPLE_CATEGORY_ID,
    }
    load_invalid_data_and_assert(ItemCreateSchema, invalid_data)


def test_item_create_schema_category_id_invalid():
    invalid_data = {
        "name": Data.SAMPLE_NAME,
        "description": Data.SAMPLE_DESCRIPTION,
        "category_id": "A",  # Not int
    }
    load_invalid_data_and_assert(ItemCreateSchema, invalid_data)


@pytest.mark.parametrize(
    "valid_name,valid_description",
    [(Data.SAMPLE_NAME, Data.SAMPLE_DESCRIPTION)]
    + Data.EDGE_CASE_VALID_NAMES_DESCRIPTION,
)
def test_item_update_schema_name_description_valid(valid_name, valid_description):
    valid_data = {
        "name": valid_name,
        "description": valid_description,
        "category_id": Data.SAMPLE_CATEGORY_ID,
    }

    item = ItemUpdateSchema().load(data=dict(data=valid_data, item_id=1))
    assert item["name"] == valid_data["name"]
    assert item["description"] == valid_data["description"]
    assert item["category_id"] == valid_data["category_id"]


def test_item_update_schema_empty_all():
    invalid_data = {}
    load_invalid_data_and_assert(
        ItemUpdateSchema, data=dict(data=invalid_data, item_id=1)
    )


@pytest.mark.parametrize("invalid_id", Data.INVALID_IDS)
def test_item_update_schema_id_invalid(invalid_id):
    invalid_data_item_id = {
        "name": Data.SAMPLE_NAME,
        "description": Data.SAMPLE_DESCRIPTION,
        "category_id": 1,
    }
    invalid_data_category_id = {
        "name": Data.SAMPLE_NAME,
        "description": Data.SAMPLE_DESCRIPTION,
        "category_id": invalid_id,
    }
    load_invalid_data_and_assert(
        ItemUpdateSchema, data=dict(data=invalid_data_item_id, item_id=invalid_id)
    )
    load_invalid_data_and_assert(
        ItemUpdateSchema, data=dict(data=invalid_data_category_id, item_id=1)
    )


def test_item_pagination_param_schema_all_valid():
    valid_data = {"page": 1, "per_page": 5, "category_id": 1}
    param = ItemPaginationParamSchema().load(valid_data)
    assert param["page"] == valid_data["page"]
    assert param["per_page"] == valid_data["per_page"]
    assert param["category_id"] == valid_data["category_id"]


def test_item_pagination_param_schema_category_id_invalid():
    invalid_data1 = {"category_id": -1}
    invalid_data2 = {"category_id": 0}
    load_invalid_data_and_assert(ItemPaginationParamSchema, invalid_data1)
    load_invalid_data_and_assert(ItemPaginationParamSchema, invalid_data2)
