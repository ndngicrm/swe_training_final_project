from flask import request

from main.commons import exceptions


def __register_user_route(app):
    from .user import UserResource, UserTokenResource

    @app.route("/users", methods=["POST"])
    def route_user():
        return UserResource.post(request.get_json())

    @app.route("/users/tokens", methods=["POST"])
    def route_user_token():
        return UserTokenResource.post(request.get_json())


def __register_category_route(app):
    from main.schemas.base import PaginationParamSchema

    from .category import CategoryResource

    @app.route("/categories", methods=["GET", "POST"])
    def route_category():
        if request.method == "GET":
            valid_args = PaginationParamSchema().load(request.args)

            if len(request.args) != len(valid_args):
                return exceptions.BadRequest(
                    error_message="Invalid query parameters."
                ).to_response()

            return CategoryResource.get(**valid_args)

        if request.method == "POST":
            return CategoryResource.post(request.get_json())

    @app.route("/categories/<string:category_id>", methods=["DELETE"])
    def route_category_with_id(category_id):
        return CategoryResource.delete(category_id)


def __register_item_route(app):
    from main.schemas.item import ItemPaginationParamSchema

    from .item import ItemResource

    @app.route("/items", methods=["GET", "POST"])
    def route_item():
        if request.method == "GET":
            valid_args = ItemPaginationParamSchema().load(request.args)

            if len(request.args) != len(valid_args):
                return exceptions.BadRequest(
                    error_message="Invalid query parameters."
                ).to_response()

            return ItemResource.get(**valid_args)

        if request.method == "POST":
            return ItemResource.post(request.get_json())

    @app.route("/items/<string:item_id>", methods=["GET", "PUT", "DELETE"])
    def route_item_with_id(item_id):
        if request.method == "GET":
            return ItemResource.get_with_id(item_id)
        if request.method == "PUT":
            return ItemResource.put(request.get_json(), item_id)
        if request.method == "DELETE":
            return ItemResource.delete(item_id)


def register_routes(app):
    __register_user_route(app)
    __register_category_route(app)
    __register_item_route(app)
