from marshmallow import ValidationError

from main.models.category import CategoryModel
from main.models.item import ItemModel
from main.models.user import UserModel
from main.schemas.category import CategorySchema
from main.schemas.item import ItemSchema
from main.schemas.user import UserSchema
from tests.data import categories_info, items_info, users_info


def test_user_schema():
    schema = UserSchema()
    sample = UserModel("a@a.com", "Aa@1234")

    # Regular cases
    user1 = schema.load(dict(email="valid1@gmail.com", password="validPassword1"))

    assert type(user1) == type(sample)
    assert user1.email == "valid1@gmail.com"

    # Invalid emails
    invalid_email = ["aaa", users_info[0][0]]
    for email in invalid_email:
        try:
            schema.load(dict(email=email, password="Aa123456"))
        except ValidationError:
            assert True
        else:
            assert False

    # Edge cases of valid passwords
    valid_passwords = ["Aa1234", "a" * 254 + "A" + "1"]
    for password in valid_passwords:
        schema.load(dict(email="valid@gmail.com", password=password))

    # Invalid passwords
    invalid_passwords = [
        "12345",
        "AAAAAA",
        "AAAAAa",
        "AAAAA1",
        "aaaaa1",
        valid_passwords[1] + "!",
    ]
    for password in invalid_passwords:
        try:
            schema.load(dict(email="valid@gmail.com", password=password))
        except ValidationError:
            assert True
        else:
            assert False


def test_category_schema():
    schema = CategorySchema()
    sample = CategoryModel("jsonify", 0)

    # Regular cases
    category1 = schema.load_with_user_id(dict(name="Valid name 1"), user_id=1)

    assert type(category1) == type(sample)
    assert category1.name == "Valid name 1"
    assert category1.user_id == 1

    # Edge cases of name (80 chars)
    long_name = "a" * 80
    schema.load_with_user_id(dict(name=long_name), user_id=2)

    # Invalid names
    invalid_names = ["", long_name + "!", categories_info[0][1]]

    for name in invalid_names:
        try:
            schema.load_with_user_id(dict(name=name), user_id=3)
        except ValidationError:
            assert True
        else:
            assert False


def test_item_schema():
    schema = ItemSchema()
    sample = ItemModel("Sample", "This is a description", 1)

    # Regular cases
    item1 = schema.load(
        dict(name="Item1", description="This is a valid description.", category_id=1)
    )

    assert type(item1) == type(sample)
    assert item1.name == "Item1"
    assert item1.description == "This is a valid description."
    assert item1.category_id == 1

    # Edge cases of name (80 chars)
    long_name = "a" * 80
    schema.load(dict(name=long_name, description="Description here.", category_id=2))

    # Invalid names
    invalid_names = ["", long_name + "!", items_info[0][0]]
    for name in invalid_names:
        try:
            schema.load(dict(name=name, description="Description", id=1))
        except ValidationError:
            assert True
        else:
            assert False

    # Edge cases of description (65536 chars)
    long_description = "a" * 65535
    schema.load(dict(name="Valid item", description=long_description, category_id=3))

    # Invalid descriptions
    invalid_descriptions = ["", long_description + "!"]
    for description in invalid_descriptions:
        try:
            schema.load(dict(name="Valid item", description=description, category_id=4))
        except ValidationError:
            assert True
        else:
            assert False
