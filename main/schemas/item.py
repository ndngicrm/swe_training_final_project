from marshmallow import ValidationError, fields, post_load, validates

from main.models.item import ItemModel
from main.schemas.base import (
    BaseSchema,
    PaginationParamSchema,
    PaginationResponseSchema,
)


class ItemSchema(BaseSchema):
    name = fields.Str(required=True, allow_none=False)
    description = fields.Str(required=True, allow_none=False)
    category_id = fields.Int(required=True, allow_none=False)
    id = fields.Int(required=False)

    @validates("name")
    def validate_name(self, name):
        if len(name) == 0 or len(name) > 80:
            raise ValidationError("Item name must be 1-80 characters in length.")
        if ItemModel.find_by_name(name):
            raise ValidationError("Item name has already been used.")

    @validates("description")
    def validate_description(self, description):
        if len(description) == 0 or len(description) > 65535:
            raise ValidationError(
                "Item description must be 1-65535 characters in length."
            )

    @post_load
    def make_item(self, data, **kwargs):
        return ItemModel(**data)


class ItemDataSchema(ItemSchema):
    name = fields.Str(required=False, allow_none=False)
    description = fields.Str(required=False, allow_none=False)
    category_id = fields.Int(required=False, allow_none=False)

    def make_item(self, data, **kwargs):
        return data


class ItemPaginationResponseSchema(PaginationResponseSchema):
    items = fields.List(fields.Nested(ItemSchema, exclude=["description"]))


class ItemPaginationParamSchema(PaginationParamSchema):
    category_id = fields.Integer()
