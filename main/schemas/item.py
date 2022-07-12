from marshmallow import ValidationError, fields, pre_load, validates, validates_schema

from main.schemas.base import (
    BaseSchema,
    PaginationParamSchema,
    PaginationResponseSchema,
)


class ItemSchema(BaseSchema):
    # For validation
    name = fields.String(required=True)
    description = fields.String(required=True)
    category_id = fields.Integer(required=True)

    # For jsonify
    id = fields.Integer(required=False)
    is_owner = fields.Boolean(required=False)

    @pre_load
    def preprocess_str(self, data, **kwargs):
        if "name" in data and isinstance(data["name"], str):
            data["name"] = data["name"].strip()
        if "description" in data and isinstance(data["description"], str):
            data["description"] = data["description"].strip()
        return data

    @validates("name")
    def validate_name(self, name):
        if len(name) == 0 or len(name) > 80:
            raise ValidationError("Item name must be 1-80 characters in length.")

    @validates("description")
    def validate_description(self, description):
        if len(description) == 0 or len(description) > 65535:
            raise ValidationError(
                "Item description must be 1-65535 characters in length."
            )


class ItemDataSchema(ItemSchema):
    name = fields.String(required=False, allow_none=False)
    description = fields.String(required=False, allow_none=False)
    category_id = fields.Integer(required=False, allow_none=False)

    @validates_schema
    def validate_schema(self, data, **kwargs):
        if (
            "name" not in data
            and "description" not in data
            and "category_id" not in data
        ):
            raise ValidationError("At least 1 field must not be empty.")


class ItemPaginationResponseSchema(PaginationResponseSchema):
    items = fields.List(fields.Nested(ItemSchema))


class ItemPaginationParamSchema(PaginationParamSchema):
    category_id = fields.Integer(required=False)

    @validates("category_id")
    def validate_category_id(self, category_id):
        if category_id < 1:
            raise ValidationError("Category ID must be at least 1.")
