import functools
from datetime import datetime, timedelta

import jwt
from flask import jsonify, request
from jwt import ExpiredSignatureError
from marshmallow import ValidationError

from main.commons import exceptions
from main.models.user import UserModel
from main.schemas.user import UserCredentialSchema, UserSchema


class UserResource:
    schema = UserSchema()

    @classmethod
    def post(cls, request_data):
        try:
            user = cls.schema.load(request_data)
        except ValidationError as error:
            return exceptions.ValidationError(error_data=error.messages).to_response()

        user.save_to_db()
        return "", 200


class UserTokenResource:
    schema = UserCredentialSchema()
    algorithm = "HS256"

    @classmethod
    def post(cls, request_data):
        try:
            user_credential = cls.schema.load(request_data)
        except ValidationError as error:
            return exceptions.ValidationError(error_data=error.messages).to_response()

        if not UserModel.is_valid_user(
            user_credential["email"], user_credential["password"]
        ):
            return exceptions.BadRequest(
                error_message="Incorrect email or password"
            ).to_response()

        user = UserModel.find_by_email(user_credential["email"])

        return jsonify(access_token=UserTokenResource.get_token(user.id))

    @classmethod
    def get_token(cls, _id):
        payload = dict(exp=datetime.now() + timedelta(minutes=30), id=_id)
        from main import app

        return jwt.encode(payload, app.secret_key, algorithm=cls.algorithm)

    @classmethod
    def get_identity_from_token(cls, token):
        from main import app

        decoded_token = jwt.decode(token, app.secret_key, algorithms=[cls.algorithm])
        print(decoded_token)
        return UserModel.find_by_id(decoded_token["id"])


def require_user_authentication(endpoint):
    from main import app

    def authenticate(func):
        @app.route(endpoint, methods=["POST"])
        @functools.wraps(func)
        def authenticator():
            jwt_token = request.headers.get["Authentication"]
            if not jwt_token:
                return exceptions.BadRequest(
                    error_message="Token expected."
                ).to_response()

            token_header, token_content = jwt_token.split()
            if token_header.strip() == "JWT":
                try:
                    user = UserTokenResource.get_identity_from_token(
                        token_content.strip()
                    )
                except ExpiredSignatureError:
                    return exceptions.BadRequest(
                        error_message="Expired token."
                    ).to_response()
                except Exception:
                    return exceptions.BadRequest(
                        error_message="Invalid token."
                    ).to_response()
                if user:
                    return func
            return exceptions.BadRequest(error_message="Invalid token.").to_response()

        return authenticator

    return authenticate
