from marshmallow import ValidationError

from main.commons import exceptions
from main.models.category import CategoryModel
from main.models.item import ItemModel
from main.resources.user import require_user_token
from main.schemas.item import ItemDataSchema, ItemPaginationResponseSchema, ItemSchema


class ItemResource:
    schema = ItemSchema()
    data_schema = ItemDataSchema()
    response_schema = ItemPaginationResponseSchema()
    max_per_page = 50

    @classmethod
    def get(cls, category_id=None, page=1, per_page=20):
        if per_page > cls.max_per_page:
            return exceptions.BadRequest(
                error_message="Too many items per page requested."
            ).to_response()

        start, stop = (page - 1) * per_page + 1, page * per_page
        if category_id:
            items = ItemModel.get_many_in_category(category_id, start, stop)
            size = ItemModel.get_size_in_category(category_id)
        else:
            items = ItemModel.get_many(start, stop)
            size = ItemModel.get_size()

        if not items:
            return exceptions.NotFound(
                error_message="No item in requested page."
            ).to_response()

        response = cls.response_schema.jsonify(
            dict(page=page, per_page=per_page, total_items=size, items=items)
        )
        return response, 200

    @classmethod
    def get_with_id(cls, _id):
        item = ItemModel.find_by_id(_id)
        if not item:
            return exceptions.NotFound(
                error_message="Item cannot be found."
            ).to_response()
        return cls.schema.jsonify(item), 200

    @classmethod
    @require_user_token
    def post(cls, request_data, user_id):
        try:
            item = cls.schema.load(request_data)
        except ValidationError as error:
            return exceptions.ValidationError(error_data=error.data).to_response()

        category = CategoryModel.find_by_id(item.category_id)
        if not category:
            return exceptions.NotFound(
                error_message="Category cannot be found."
            ).to_response()

        if category.user_id != user_id:
            return exceptions.Forbidden(
                error_message="No permission to add item in this category."
            ).to_response()

        item.save_to_db()
        return dict(id=item.id), 200

    @classmethod
    @require_user_token
    def put(cls, request_data, item_id, user_id):
        item = ItemModel.find_by_id(item_id)
        if not item:
            return exceptions.NotFound(
                error_message="Item cannot be found."
            ).to_response()

        try:
            new_item_data = cls.data_schema.load(request_data)
        except ValidationError as error:
            return exceptions.ValidationError(error_data=error.messages).to_response()

        if "name" in new_item_data:
            item.name = new_item_data["name"]
        if "description" in new_item_data:
            item.description = new_item_data["description"]
        if "category_id" in new_item_data:
            category = CategoryModel.find_by_id(new_item_data["category_id"])
            if user_id != category.user_id:
                return exceptions.Forbidden(
                    error_message="No permission to edit item in this category."
                ).to_response()
            item.category = new_item_data["category_id"]

        item.save_to_db()
        return cls.schema.jsonify(item), 200

    @classmethod
    @require_user_token
    def delete(cls, item_id, user_id):
        item = ItemModel.find_by_id(item_id)
        if not item:
            return exceptions.NotFound(
                error_message="Item cannot be found."
            ).to_response()
        category = CategoryModel.find_by_id(item.category_id)
        if category.user_id != user_id:
            return exceptions.Forbidden(
                error_message="No permission to delete item in this category."
            ).to_response()
        item.delete_from_db()
        return "", 200
