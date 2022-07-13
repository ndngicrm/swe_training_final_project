from datetime import datetime, timedelta

import jwt
import pytest

from main.commons.exceptions import Unauthorized
from main.schemas.token import (
    TokenBaseSchema,
    TokenCredentialSchema,
    TokenDecodeSchema,
    TokenEncodeSchema,
)
from tests.schemas.common import load_invalid_data_and_assert


class Data:
    SAMPLE_EMAIL = "valid@email.com"
    SAMPLE_PASSWORD = "ValidPassword1"
    ALGORITHM = TokenBaseSchema.algorithm

    class TokenCredentialSchema:
        INVALID_EMAILS = [
            1,  # Not sring
            "adsnasdnas",  # Lack @, *.*
            "daslkdnals.com",  # Lack @
            "asdnjams@",  # Lack *.*
            "almost@valid",  # Lack .*
        ]

    class TokenDecodeSchema:
        INVALID_TOKENS = [
            "dansjklcas",  # Wrong structure
            "JWT " + TokenEncodeSchema().load(dict(id=1))["token"],  # Wrong heading
            "Bearer ndsaijklmasasjdna.dasoiknca",  # Wrong token
        ]


def test_token_credential_schema_email_and_password_valid():
    valid_data = {"email": Data.SAMPLE_EMAIL, "password": Data.SAMPLE_PASSWORD}
    valid_credential = TokenCredentialSchema().load(valid_data)
    assert valid_credential["email"] == valid_data["email"]
    assert valid_credential["password"] == valid_data["password"]


@pytest.mark.parametrize("invalid_email", Data.TokenCredentialSchema.INVALID_EMAILS)
def test_token_credential_schema_email_invalid(invalid_email):
    invalid_data = {"email": invalid_email, "password": Data.SAMPLE_PASSWORD}
    load_invalid_data_and_assert(TokenCredentialSchema, invalid_data)


def test_token_credential_schema_password_trimming():
    spaced_data = {
        "email": Data.SAMPLE_EMAIL,
        "password": "  " + Data.SAMPLE_PASSWORD + "  ",
    }
    valid_credential = TokenCredentialSchema().load(spaced_data)
    assert valid_credential["password"] == Data.SAMPLE_PASSWORD


def test_token_decode_schema_token_valid(app):
    token = "Bearer " + jwt.encode(
        dict(exp=datetime.now() + timedelta(minutes=30), iss=1),
        app.secret_key,
        algorithm=Data.ALGORITHM,
    )
    data = TokenDecodeSchema().load(dict(token=token))
    assert data["id"] == 1


@pytest.mark.parametrize("invalid_token", Data.TokenDecodeSchema.INVALID_TOKENS)
def test_token_decode_schema_token_invalid(invalid_token):
    load_invalid_data_and_assert(TokenDecodeSchema, dict(token=invalid_token))


def test_token_decode_schema_token_expired(app):
    expired_token = "Bearer " + jwt.encode(
        dict(exp=1, iss=1),  # some abitrary small number = small time
        app.secret_key,
        algorithm=Data.ALGORITHM,
    )
    try:
        TokenDecodeSchema().load(dict(token=expired_token))
    except Unauthorized:
        assert True
    else:
        assert False


def test_token_encode_schema_id_valid():
    id = 1
    token = "Bearer " + TokenEncodeSchema().load(dict(id=id))["token"]
    data = TokenDecodeSchema().load(dict(token=token))
    assert id == data["id"]


def test_token_encode_schema_id_invalid():
    # String, not int
    load_invalid_data_and_assert(TokenEncodeSchema, dict(id="A"))
    # ID smaller than 1
    load_invalid_data_and_assert(TokenEncodeSchema, dict(id=0))
