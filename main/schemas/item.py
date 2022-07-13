from marshmallow import ValidationError, fields, pre_load, validates, validates_schema

from main.schemas.base import (
    BaseSchema,
    PaginationParamSchema,
    PaginationResponseSchema,
)


class ItemBaseSchema(BaseSchema):
    name = fields.String(required=False)
    description = fields.String(required=False)
    category_id = fields.Integer(required=False)

    @pre_load
    def preprocess_str(self, data, **_):
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

    @validates("category_id")
    def validate_category_id(self, category_id):
        if category_id < 1:
            raise ValidationError("Category ID must be at least 1.")


class ItemCreateSchema(ItemBaseSchema):
    name = fields.String(required=True)
    description = fields.String(required=True)
    category_id = fields.Integer(required=True)


class ItemUpdateSchema(ItemBaseSchema):
    id = fields.Integer(required=False)

    @pre_load
    def unpack(self, data, **_):
        """
        Data send to ItemResource PUT should have the format
        ```
        {
            data: <request_data>,
            item_id: <item_id>
        }
        ```
        Doing this to avoid user append invalid `id` within request data instead
        of endpoint
        """
        item_id = data["item_id"]
        data = data["data"]
        if "id" in data:
            raise ValidationError(dict(id=["Unknown field."]))
        data["id"] = item_id
        return data

    @validates("id")
    def validate_id(self, id):
        if id < 1:
            raise ValidationError("Item ID must be at least 1")

    @validates_schema
    def validate_schema(self, data, **_):
        if (
            "name" not in data
            and "description" not in data
            and "category_id" not in data
        ):
            raise ValidationError("At least 1 field must not be empty.")


class ItemResponseSchema(ItemBaseSchema):
    id = fields.Integer(required=False)
    is_owner = fields.Boolean(required=False)


class ItemPaginationParamSchema(PaginationParamSchema):
    category_id = fields.Integer(required=False)

    @validates("category_id")
    def validate_category_id(self, category_id):
        if category_id < 1:
            raise ValidationError("Category ID must be at least 1.")


class ItemPaginationResponseSchema(PaginationResponseSchema):
    items = fields.List(fields.Nested(ItemResponseSchema))
