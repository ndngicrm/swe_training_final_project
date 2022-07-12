from main.commons.decorators import check_no_instance_existed, load_data_with_schema
from main.models.user import UserModel
from main.schemas.user import UserSchema


class UserResource:
    @classmethod
    @load_data_with_schema(UserSchema())
    @check_no_instance_existed(UserModel, attrs=["email"])
    def post(cls, *, data, **kwargs):
        user = UserModel(**data)
        user.save_to_db()
        return dict()
