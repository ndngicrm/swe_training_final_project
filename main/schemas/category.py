from marshmallow import ValidationError, fields, pre_load, validates

from main.schemas.base import BaseSchema, PaginationResponseSchema


class CategorySchema(BaseSchema):
    # For validation
    name = fields.String(required=True)

    # For jsonify
    id = fields.Integer(required=False)
    is_owner = fields.Boolean(required=False)

    @pre_load
    def preprocess_str(self, data, **kwargs):
        if "name" in data and isinstance(data["name"], str):
            data["name"] = data["name"].strip()
        return data

    @validates("name")
    def validate_name(self, name):
        if len(name) == 0 or len(name) > 80:
            raise ValidationError(
                "Category name must be between 1-80 characters in length."
            )


class CategoryPaginationResponseSchema(PaginationResponseSchema):
    categories = fields.List(fields.Nested(CategorySchema))
