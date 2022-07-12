from main.commons.decorators import (
    load_data_with_schema,
    need_existing_attrs,
    need_user_token,
    validate_unique_attrs,
)
from main.commons.exceptions import Forbidden
from main.models.category import CategoryModel
from main.models.item import ItemModel
from main.models.user import UserModel
from main.schemas.item import (
    ItemDataSchema,
    ItemPaginationParamSchema,
    ItemPaginationResponseSchema,
    ItemSchema,
)


class ItemResource:
    class __ItemResourceHandler:
        def check_category_permssion(self, user_id, category_id, mode="error"):
            @need_existing_attrs(CategoryModel, attrs=["id"])
            def check_permission(data, **kwargs):
                category = kwargs["existed"]["id"]
                print(mode)
                if mode == "boolean":
                    return True if category.user_id == user_id else False
                if mode == "error":
                    if category.user_id != user_id:
                        raise Forbidden(
                            error_message="No permission to edit/delete in category"
                        )

            return check_permission(data=dict(id=category_id))

        def check_category_exist(self, category_id):
            @need_existing_attrs(CategoryModel, attrs=["id"])
            def check_category(**kwargs):
                pass

            check_category(data=dict(id=category_id))

    handler = __ItemResourceHandler()

    @classmethod
    @need_user_token(UserModel, mode="optional")
    @load_data_with_schema(ItemPaginationParamSchema())
    def get(cls, *, data, **kwargs):
        tmp_params = dict()
        if "category_id" in data:
            cls.handler.check_category_exist(data["category_id"])
            tmp_params["category_id"] = data["category_id"]

        items = ItemModel.get_many(start=data["start"], stop=data["stop"], **tmp_params)
        print(items)

        if items:
            schema = ItemSchema()
            new_items = list()
            for item in items:
                item_data = schema.dump(item)
                if "user_id" in kwargs:
                    item_data["is_owner"] = cls.handler.check_category_permssion(
                        kwargs["user_id"], item.category_id, mode="boolean"
                    )
                else:
                    item_data["is_owner"] = False
                new_items.append(schema.load(item_data))
            items = new_items
        else:
            items = list()

        size = ItemModel.get_size(**tmp_params)

        return ItemPaginationResponseSchema().jsonify(
            dict(
                page=data["page"],
                per_page=data["per_page"],
                total_items=size,
                items=items,
            )
        )

    @classmethod
    @need_user_token(UserModel, mode="optional")
    @need_existing_attrs(ItemModel, attrs=["id"])
    def get_with_id(cls, *, data, **kwargs):
        item = kwargs["existed"]["id"]

        schema = ItemSchema()
        item_data = schema.dump(item)
        if "user_id" in kwargs:
            item_data["is_owner"] = cls.handler.check_category_permssion(
                kwargs["user_id"], item.category_id, mode="boolean"
            )
        else:
            item_data["is_owner"] = False

        return schema.load(item_data)

    @classmethod
    @need_user_token(UserModel)
    @load_data_with_schema(ItemSchema())
    @validate_unique_attrs(ItemModel, attrs=["name"])
    def post(cls, *, data, **kwargs):
        user_id = kwargs["user_id"]
        cls.handler.check_category_exist(data["category_id"])
        cls.handler.check_category_permssion(user_id, data["category_id"])
        item = ItemModel(**data)
        item.save_to_db()
        return dict(id=item.id)

    @classmethod
    @need_user_token(UserModel)
    @load_data_with_schema(ItemDataSchema())
    @need_existing_attrs(ItemModel, attrs=["id"])
    def put(cls, *, data, **kwargs):
        user_id = kwargs["user_id"]
        item = kwargs["existed"]["id"]

        cls.handler.check_category_permssion(user_id, item.category_id)

        if "category_id" in data:
            cls.handler.check_category_exist(data["category_id"])
            cls.handler.check_category_permssion(user_id, data["category_id"])
            item.category_id = data["category_id"]

        item.name = data["name"] if "name" in data else item.name
        item.description = (
            data["description"] if "description" in data else item.description
        )

        item.save_to_db()
        return ItemSchema().jsonify(item)

    @classmethod
    @need_user_token(UserModel)
    @need_existing_attrs(ItemModel, attrs=["id"])
    def delete(cls, *, data, **kwargs):
        user_id = kwargs["user_id"]
        item = kwargs["existed"]["id"]
        cls.handler.check_category_permssion(user_id, item.category_id)
        item.delete_from_db()
        return dict()
