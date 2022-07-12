from main.commons.decorators import load_data_with_schema, need_user_token
from main.commons.exceptions import Unauthorized
from main.models.user import UserModel
from main.schemas.token import TokenCredentialSchema, TokenEncodeSchema


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
        def get_token(**kwargs):
            return kwargs["data"]["token"]

        return get_token(data=dict(id=id))

    @classmethod
    def get_id_from_token(cls, token):
        @need_user_token(UserModel, str="optional")
        def get_id_from_token(**kwargs):
            return kwargs["user_id"]

        return get_id_from_token(data=dict(token=token))
