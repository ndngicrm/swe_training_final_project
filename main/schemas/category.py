from marshmallow import ValidationError, fields, post_load, pre_load, validates

from main.models.category import CategoryModel
from main.schemas.base import BaseSchema, PaginationResponseSchema


class CategorySchema(BaseSchema):
    name = fields.Str(required=True, allow_none=False)
    id = fields.Int(
        required=False, allow_none=False
    )  # not needed for validation but required for jsonify
    __user_id = None

    @pre_load(pass_many=True)
    def make_data(self, data, **kwargs):
        self.__user_id = data["user_id"]
        return data["data"]

    def load_with_user_id(self, data, user_id):
        return self.load(dict(data=data, user_id=user_id))

    @validates("name")
    def validate_name(self, name):
        if len(name) == 0 or len(name) > 80:
            raise ValidationError(
                "Category name must be between 1-80 characters in length."
            )
        if CategoryModel.find_by_name(name):
            raise ValidationError("Category name has already been used.")

    @post_load(pass_many=True)
    def make_category(self, data, **kwargs):
        return CategoryModel(data["name"], self.__user_id)


class CategoryPaginationResponseSchema(PaginationResponseSchema):
    categories = fields.List(fields.Nested(CategorySchema))
