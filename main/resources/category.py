from main.commons.decorators import (
    check_no_instance_existed,
    load_data_with_schema,
    need_existing_instance,
    need_user_token,
    secure_sql_error,
)
from main.commons.exceptions import Forbidden
from main.models.category import CategoryModel
from main.models.user import UserModel
from main.schemas.base import PaginationParamSchema
from main.schemas.category import (
    CategoryBaseSchema,
    CategoryPaginationResponseSchema,
    CategoryResponseSchema,
)


class CategoryResource:
    class __CategoryResourceHandler:
        @secure_sql_error
        def check_permission(self, user_id, category):
            if category.user_id != user_id:
                raise Forbidden(error_message="No permission to edit the category.")

    handler = __CategoryResourceHandler()

    @classmethod
    @need_user_token(UserModel, mode="optional")
    @load_data_with_schema(PaginationParamSchema())
    def get(cls, *, data, **kwargs):
        categories = CategoryModel.get_many(data["start"], data["stop"])

        if categories:
            new_categories = list()
            for category in categories:
                category_data = CategoryResponseSchema().dump(category)
                category_data["is_owner"] = (
                    category.user_id == kwargs["user_id"]
                    if "user_id" in kwargs
                    else False
                )
                new_categories.append(category_data)

            categories = new_categories
        else:
            categories = list()

        return CategoryPaginationResponseSchema().jsonify(
            dict(
                page=data["page"],
                per_page=data["per_page"],
                total_items=CategoryModel.get_size(),
                categories=categories,
            )
        )

    @classmethod
    @need_user_token(UserModel)
    @load_data_with_schema(CategoryBaseSchema())
    @check_no_instance_existed(CategoryModel, attrs=["name"])
    def post(cls, *, data, **kwargs):
        user_id = kwargs["user_id"]
        category = CategoryModel(data["name"], user_id)
        category.save_to_db()

        category_data = CategoryResponseSchema().dump(category)
        category_data["is_owner"] = True

        return CategoryResponseSchema().jsonify(category_data)

    @classmethod
    @need_user_token(UserModel)
    @need_existing_instance(CategoryModel, attrs=["id"])
    def delete(cls, *, data, **kwargs):
        category = kwargs["existed"]["id"]
        user_id = kwargs["user_id"]
        cls.handler.check_permission(user_id, category)
        category.delete_from_db()
        return dict()
