from main.commons.decorators import load_data_with_schema, validate_unique_attrs
from main.models.user import UserModel
from main.schemas.user import UserSchema


class UserResource:
    @classmethod
    @load_data_with_schema(UserSchema())
    @validate_unique_attrs(UserModel, attrs=["email"])
    def post(cls, *, data, **kwargs):
        user = UserModel(**data)
        user.save_to_db()
        return dict()
