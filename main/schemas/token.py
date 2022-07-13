from datetime import datetime, timedelta

import jwt
from marshmallow import ValidationError, fields, post_load, pre_load, validates

from main.commons.exceptions import Unauthorized

from .base import BaseSchema


class TokenCredentialSchema(BaseSchema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

    @pre_load
    def preprocess_password(self, data, **_):
        if "password" in data and isinstance(data["password"], str):
            data["password"] = data["password"].strip()
        return data


class TokenBaseSchema(BaseSchema):
    algorithm = "HS256"


class TokenDecodeSchema(TokenBaseSchema):
    token = fields.String(required=True)

    @pre_load
    def extract_content(self, data, **_):
        if "token" in data and isinstance(data["token"], str):
            token_parts = data["token"].split()
            if len(token_parts) != 2 or token_parts[0].strip() != "Bearer":
                raise ValidationError("Invalid token.", field_name="token")
            data["token"] = token_parts[1].strip()
        return data

    @post_load
    def make_identity(self, data, **_):
        from main import app

        try:
            decoded = jwt.decode(
                data["token"], app.secret_key, algorithms=[self.algorithm]
            )
            iss = decoded["iss"]
        except jwt.ExpiredSignatureError:
            raise Unauthorized(error_message="Expired token.")
        except Exception:
            raise ValidationError("Invalid token.", field_name="token")
        data["id"] = iss
        return data


class TokenEncodeSchema(TokenBaseSchema):
    id = fields.Integer(required=True)

    @validates("id")
    def validate_id(self, id):
        if id < 1:
            raise ValidationError("User ID must be greater than 1.")

    @post_load
    def make_token(self, data, **_):
        from main import app

        payload = dict(exp=datetime.now() + timedelta(minutes=30), iss=data["id"])
        data["token"] = jwt.encode(payload, app.secret_key, algorithm=self.algorithm)
        return data
