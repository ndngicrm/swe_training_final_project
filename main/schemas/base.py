from flask import jsonify
from marshmallow import RAISE, Schema, ValidationError, fields, post_load, validates


class BaseSchema(Schema):
    class Meta:
        unknown = RAISE

    def jsonify(self, obj, many=False):
        return jsonify(self.dump(obj, many=many))


class PaginationResponseSchema(BaseSchema):
    per_page = fields.Integer()
    page = fields.Integer()
    total_items = fields.Integer()


class PaginationParamSchema(BaseSchema):
    per_page = fields.Integer(load_default=20)
    page = fields.Integer(load_default=1)
    __max_per_page = 50

    @validates("per_page")
    def validate_per_page(self, per_page):
        if per_page < 1:
            raise ValidationError("Invalid value.")
        if per_page > self.__max_per_page:
            raise ValidationError("Too many item requested.")

    @validates("page")
    def validate_page(self, page):
        if page < 1:
            raise ValidationError("Invalid value.")

    @post_load
    def add_slice(self, data, **_):
        data["start"] = (data["page"] - 1) * data["per_page"] + 1
        data["stop"] = data["page"] * data["per_page"]
        return data


class SimpleIdSchema(BaseSchema):
    id = fields.Integer(required=True)

    @validates("id")
    def validate_id(self, id):
        if id < 1:
            raise ValidationError("ID must be at least 1.")
