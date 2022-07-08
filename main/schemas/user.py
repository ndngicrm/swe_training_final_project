from marshmallow import ValidationError, fields, post_load, validates

from main.models.user import UserModel
from main.schemas.base import BaseSchema


class UserSchema(BaseSchema):
    email = fields.Email(required=True, allow_none=False)
    password = fields.Str(required=True, allow_none=False)

    @validates("email")
    def validate_email(self, email):
        if UserModel.find_by_email(email):
            raise ValidationError("Email has already been used.")

    @validates("password")
    def validate_password(self, password):
        if len(password) < 6 or len(password) > 256:
            raise ValidationError("Password must be 6-256 characters in length.")
        if not any(password_char.isupper() for password_char in password):
            raise ValidationError("Password must contain at least 1 upper character.")
        if not any(password_char.islower() for password_char in password):
            raise ValidationError("Password must contain at least 1 lower character.")
        if not any(password_char.isdigit() for password_char in password):
            raise ValidationError("Password must contain at least 1 digit.")

    @post_load
    def make_user(self, data, **kwargs):
        return UserModel(**data)


class UserCredentialSchema(BaseSchema):
    email = fields.Email(required=True, allow_none=False)
    password = fields.Str(required=True, allow_none=False)
