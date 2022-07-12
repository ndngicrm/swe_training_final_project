import pytest

from main.schemas.user import UserSchema
from tests.schemas.common import load_invalid_data_and_assert


class Data:
    SAMPLE_EMAIL = "valid@gmail.com"
    SAMPLE_PASSWORD = "ValidPassword1"
    EDGE_CASES_VALID_PASSWORDS = ["a" * 4 + "A" + "1", "a" * 254 + "A" + "1"]
    INVALID_EMAILS = [
        1,  # Not string
        "adsnasdnas",  # Lack @, *.*
        "daslkdnals.com",  # Lack @
        "asdnjams@",  # Lack *.*
        "almost@valid",  # Lack .*
    ]
    INVALID_PASSWORDS = [
        1,  # Not string
        "♞" * 6,  # Not ascii
        "a" * 5,  # Too short
        "a" * 257,  # Too long
        "a" * 10,  # Lack upper, digit
        "A" * 10,  # Lack lower, digit
        "1" * 10,  # Lack upper, lower
        "A" * 10 + "a",  # Lack digit
        "A" * 10 + "1",  # Lack lower
        "a" * 10 + "1",  # Lack upper
    ]


def test_sth():
    assert 1


@pytest.mark.parametrize(
    "valid_password", [Data.SAMPLE_PASSWORD] + Data.EDGE_CASES_VALID_PASSWORDS
)
def test_email_and_password_valid(valid_password):
    valid_data = {"email": Data.SAMPLE_EMAIL, "password": valid_password}
    user = UserSchema().load(valid_data)
    assert user["email"] == valid_data["email"]
    assert user["password"] == valid_data["password"]


@pytest.mark.parametrize("invalid_email", Data.INVALID_EMAILS)
def test_email_invalid(invalid_email):
    invalid_data = {"email": invalid_email, "password": Data.SAMPLE_PASSWORD}
    load_invalid_data_and_assert(UserSchema, invalid_data)


@pytest.mark.parametrize("invalid_password", Data.INVALID_PASSWORDS)
def test_password_invalid(invalid_password):
    invalid_data = {"email": Data.SAMPLE_EMAIL, "password": invalid_password}
    load_invalid_data_and_assert(UserSchema, invalid_data)


def test_password_space_trimming():
    spaced_data = {
        "email": Data.SAMPLE_EMAIL,
        "password": "  " + Data.SAMPLE_PASSWORD + "  ",
    }
    user = UserSchema().load(spaced_data)
    assert user["password"] == Data.SAMPLE_PASSWORD
