from functools import wraps

from flask import request
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from main.commons.exceptions import BadRequest, InternalServerError, NotFound
from main.commons.exceptions import ValidationError as _ValidationError
from main.schemas.token import TokenDecodeSchema


def catch_validation_error_data(func):
    """
    Raise `ValidationError` with custom error data.
    """

    @wraps(func)
    def execute_and_catch(*arg, **kwargs):
        try:
            return func(*arg, **kwargs)
        except ValidationError as error:
            raise _ValidationError(error_data=error.messages)

    return execute_and_catch


def secure_sql_error(func):
    # return func
    """
    Raise Internal Server Error with error name instead of error trace. Use before
    all SQL queries of Model.
    """

    @wraps(func)
    def execute_and_catch(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as error:
            raise InternalServerError(
                error_message=f"SQL Error: {type(error).__name__}"
            )

    return execute_and_catch


def load_data_with_schema(schema):
    """
    Apply the schema to the specified kwarg `data`. If no `ValidationError` is
    raised, then append loaded data into kwarg `data` of decorated function.
    """

    def wrapper(func):
        @wraps(func)
        @catch_validation_error_data
        def excecute_and_append(*args, **kwargs):
            kwargs["data"] = schema.load(kwargs["data"])
            return func(*args, **kwargs)

        return excecute_and_append

    return wrapper


def check_no_instance_existed(Model, attrs=[]):
    """
    Make sure each key in `attrs` has a unique instance in the `Model`. Otherwise,
    raise `ValidationError`. Take values from kwarg `data`.
    """

    def wrapper(func):
        @wraps(func)
        @catch_validation_error_data
        @secure_sql_error
        def execute(*args, **kwargs):
            data = kwargs["data"]
            # Preserve order of validation as listed in `attrs`
            intersect = [key for key in attrs if key in data]
            for key in intersect:
                if Model.find_by_attributes(**{key: data[key]}):
                    raise ValidationError(
                        {key: [f"{key.capitalize()} has already been used."]}
                    )
            return func(*args, **kwargs)

        return execute

    return wrapper


def need_existing_instance(Model, attrs=[], tag=None):
    """
    Make sure at least one key in `attrs` have at least one instance. Otherwise,
    raise `ValidationError`. Take data from kwarg `data`. Append `existed` as a
    dictionary of existing instance.
    """
    if not tag:
        tag = Model.__tablename__.capitalize()

    def wrapper(func):
        @wraps(func)
        @catch_validation_error_data
        @secure_sql_error
        def execute(*args, **kwargs):
            data = kwargs["data"]
            intersect = set(attrs) & set(data.keys())
            existed = dict()
            for key in intersect:
                object = Model.find_by_attributes(**{key: data[key]})
                if object:
                    existed[key] = object
            if not existed:
                raise NotFound(error_message=f"{tag} cannot be found.")
            kwargs["existed"] = existed
            return func(*args, **kwargs)

        return execute

    return wrapper


def need_user_token(UserModel, mode="required"):
    """
    Make sure the resource is accessed with appropriate `user_id`. If
    `mode="required"`, user must have token to access resource. Otherwise, raise
    `BadRequest`. If `mode="optional"`, user may not use token to access resource.
    However, adding token can provide more information of the resource.
    """

    def wrapper(func):
        @load_data_with_schema(TokenDecodeSchema())
        @need_existing_instance(UserModel, attrs=["id"])
        def decode_token(**kwargs):
            user = kwargs["existed"]["id"]
            return user.id

        @wraps(func)
        def authenticate(*args, **kwargs):
            token = request.headers.get("Authorization")
            if token:
                user_id = decode_token(data=dict(token=token))
                kwargs["user_id"] = user_id
            elif mode != "optional":
                raise BadRequest(error_message="Token expected.")
            return func(*args, **kwargs)

        return authenticate

    return wrapper
