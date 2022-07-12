from flask import request

from main.schemas.base import SimpleIdSchema


def __register_user_route(app):
    from .user import UserResource

    @app.route("/users", methods=["POST"])
    def route_user():
        return UserResource.post(data=request.get_json())


def __register_token_route(app):
    from .token import TokenResource

    @app.route("/access-tokens", methods=["POST"])
    def route_token():
        return TokenResource.post(data=request.get_json())


def __register_category_route(app):
    from .category import CategoryResource

    @app.route("/categories", methods=["GET", "POST"])
    def route_category():
        if request.method == "GET":
            return CategoryResource.get(data=request.args.to_dict())

        if request.method == "POST":
            return CategoryResource.post(data=request.get_json())

    @app.route("/categories/<int:category_id>", methods=["DELETE"])
    def route_category_with_id(category_id):
        SimpleIdSchema().validate(dict(id=category_id))
        return CategoryResource.delete(data=dict(id=category_id))


def __register_item_route(app):
    from .item import ItemResource

    @app.route("/items", methods=["GET", "POST"])
    def route_item():
        if request.method == "GET":
            return ItemResource.get(data=request.args.to_dict())

        if request.method == "POST":
            return ItemResource.post(data=request.get_json())

    @app.route("/items/<int:item_id>", methods=["GET", "PUT", "DELETE"])
    def route_item_with_id(item_id):
        SimpleIdSchema().validate(dict(id=item_id))
        if request.method == "GET":
            return ItemResource.get_with_id(data=dict(id=item_id))
        if request.method == "PUT":
            data = request.get_json()
            data["id"] = item_id
            return ItemResource.put(data=data)
        if request.method == "DELETE":
            return ItemResource.delete(data=dict(id=item_id))


def register_routes(app):
    __register_user_route(app)
    __register_token_route(app)
    __register_category_route(app)
    __register_item_route(app)
