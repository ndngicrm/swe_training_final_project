from marshmallow import ValidationError

from main.commons.decorators import (
    check_no_instance_existed,
    load_data_with_schema,
    need_existing_instance,
    need_user_token,
)
from main.commons.exceptions import Forbidden
from main.models.category import CategoryModel
from main.models.item import ItemModel
from main.models.user import UserModel
from main.schemas.item import (
    ItemCreateSchema,
    ItemPaginationParamSchema,
    ItemPaginationResponseSchema,
    ItemResponseSchema,
    ItemUpdateSchema,
)


class ItemResource:
    class __ItemResourceHandler:
        def check_category_permission(self, user_id, category_id, mode="error"):
            @need_existing_instance(CategoryModel, attrs=["id"])
            def check_permission(data, **kwargs):
                category = kwargs["existed"]["id"]
                if mode == "boolean":
                    return True if category.user_id == user_id else False
                if mode == "error":
                    if category.user_id != user_id:
                        raise Forbidden(
                            error_message="No permission to edit/delete in category"
                        )

            return check_permission(data=dict(id=category_id))

        def check_category_exist(self, category_id):
            check_category = need_existing_instance(CategoryModel, attrs=["id"])(
                lambda data, **_: None
            )
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

        if items:
            new_items = list()
            for item in items:
                item_data = ItemResponseSchema().dump(item)
                if "user_id" in kwargs:
                    item_data["is_owner"] = cls.handler.check_category_permission(
                        kwargs["user_id"], item.category_id, mode="boolean"
                    )
                else:
                    item_data["is_owner"] = False
                # new_items.append(cls.schema.load(item_data))
                new_items.append(item_data)
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
    @need_existing_instance(ItemModel, attrs=["id"])
    def get_with_id(cls, *, data, **kwargs):
        item = kwargs["existed"]["id"]

        item_data = ItemResponseSchema().dump(item)
        if "user_id" in kwargs:
            item_data["is_owner"] = cls.handler.check_category_permission(
                kwargs["user_id"], item.category_id, mode="boolean"
            )
        else:
            item_data["is_owner"] = False

        return ItemResponseSchema().jsonify(item_data)

    @classmethod
    @need_user_token(UserModel)
    @load_data_with_schema(ItemCreateSchema())
    @check_no_instance_existed(ItemModel, attrs=["name"])
    def post(cls, *, data, **kwargs):
        user_id = kwargs["user_id"]
        cls.handler.check_category_exist(data["category_id"])
        cls.handler.check_category_permission(user_id, data["category_id"])
        item = ItemModel(**data)
        item.save_to_db()

        item_data = ItemResponseSchema().dump(item)
        item_data["is_owner"] = True

        return ItemResponseSchema().jsonify(item_data)

    @classmethod
    @need_user_token(UserModel)
    @load_data_with_schema(ItemUpdateSchema())
    @need_existing_instance(ItemModel, attrs=["id"])
    def put(cls, *, data, **kwargs):
        user_id = kwargs["user_id"]
        item = kwargs["existed"]["id"]

        cls.handler.check_category_permission(user_id, item.category_id)

        if "category_id" in data:
            cls.handler.check_category_exist(data["category_id"])
            cls.handler.check_category_permission(user_id, data["category_id"])
            item.category_id = data["category_id"]

        if "name" in data and item.name != data["name"]:
            if ItemModel.find_by_attributes(**dict(name=data["name"])):
                raise ValidationError(dict(name=["Name has already been used."]))
            item.name = data["name"]

        item.description = (
            data["description"] if "description" in data else item.description
        )

        item.save_to_db()

        item_data = ItemResponseSchema().dump(item)
        item_data["is_owner"] = True

        return ItemResponseSchema().jsonify(item_data)

    @classmethod
    @need_user_token(UserModel)
    @need_existing_instance(ItemModel, attrs=["id"])
    def delete(cls, *, data, **kwargs):
        user_id = kwargs["user_id"]
        item = kwargs["existed"]["id"]
        cls.handler.check_category_permission(user_id, item.category_id)
        item.delete_from_db()
        return dict()
