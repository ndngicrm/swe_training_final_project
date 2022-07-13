from main.commons.decorators import load_data_with_schema
from main.commons.exceptions import Unauthorized
from main.models.user import UserModel
from main.schemas.token import (
    TokenCredentialSchema,
    TokenDecodeSchema,
    TokenEncodeSchema,
)


class TokenResource:
    @classmethod
    @load_data_with_schema(TokenCredentialSchema())
    def post(cls, *, data, **kwargs):
        if not UserModel.is_valid_user(data["email"], data["password"]):
            raise Unauthorized(error_message="Incorrect email or password.")

        user = UserModel.find_by_attributes(email=data["email"])
        return dict(access_token=cls.get_token(user.id))

    @classmethod
    def get_token(cls, id):
        @load_data_with_schema(TokenEncodeSchema())
        def get_token_with_schema(data, **kwargs):
            return data["token"]

        return get_token_with_schema(data=dict(id=id))

    @classmethod
    def get_id_from_token(cls, token):
        @load_data_with_schema(TokenDecodeSchema())
        def get_id_with_schema(data, **kwargs):
            return data["id"]

        return get_id_with_schema(data=dict(token=token))
