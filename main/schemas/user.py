from marshmallow import ValidationError, fields, pre_load, validates

from main.schemas.base import BaseSchema


class UserSchema(BaseSchema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

    @pre_load
    def preprocess_password(self, data, **kwargs):
        data["password"] = data["password"].strip()
        return data

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
