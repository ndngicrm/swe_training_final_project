from flask import request


def register_routes(app):
    from .resources.user import UserResource, UserTokenResource

    @app.route("/users", methods=["POST"])
    def route_user():
        return UserResource.post(request.get_json())

    @app.route("/users/tokens", methods=["POST"])
    def route_user_token():
        return UserTokenResource.post(request.get_json())
