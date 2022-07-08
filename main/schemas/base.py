from flask import jsonify
from marshmallow import EXCLUDE, Schema, fields


class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    def jsonify(self, obj, many=False):
        return jsonify(self.dump(obj, many=many))


class PaginationResponseSchema(BaseSchema):
    per_page = fields.Integer()
    page = fields.Integer()
    total_items = fields.Integer()


class PaginationParamSchema(BaseSchema):
    per_page = fields.Integer()
    page = fields.Integer()
