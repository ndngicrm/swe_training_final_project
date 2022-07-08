from marshmallow import ValidationError

from main.commons import exceptions
from main.models.category import CategoryModel
from main.resources.user import require_user_token
from main.schemas.category import CategoryPaginationResponseSchema, CategorySchema


class CategoryResource:
    schema = CategorySchema()
    response_schema = CategoryPaginationResponseSchema()
    max_per_page = 50

    @classmethod
    def get(cls, page=1, per_page=20):
        if per_page > cls.max_per_page:
            return exceptions.BadRequest(
                error_message="Too many items per page requested."
            ).to_response()

        start, stop = (page - 1) * per_page + 1, page * per_page
        categories = CategoryModel.get_many(start, stop)

        if not categories:
            return exceptions.NotFound(
                error_message="No item in requested page."
            ).to_response()

        response = cls.response_schema.jsonify(
            dict(
                page=page,
                per_page=per_page,
                total_items=CategoryModel.get_size(),
                categories=categories,
            )
        )
        return response, 200

    @classmethod
    @require_user_token
    def post(cls, request_data, user_id):
        try:
            category = cls.schema.load_with_user_id(request_data, user_id)
        except ValidationError as error:
            return exceptions.ValidationError(error_data=error.messages).to_response()
        category.save_to_db()
        return dict(id=category.id), 200

    @classmethod
    @require_user_token
    def delete(cls, category_id, user_id):
        category = CategoryModel.find_by_id(category_id)
        if category:
            if category.user_id == user_id:
                category.delete_from_db()
                return "", 200
            return exceptions.Forbidden(
                error_message="Only category's owner can delete."
            ).to_response()
        return exceptions.NotFound(
            error_message="Category cannot be found."
        ).to_response()
