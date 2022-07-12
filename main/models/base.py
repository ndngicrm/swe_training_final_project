from functools import wraps

from main import db
from main.commons.decorators import secure_sql_error


def filter_by_allowed_attributes(func):
    """
    Decorator for `QueryMixin` classes' classmethods only.

    Return `None` if any of `kwargs` is not in `QueryMixin.filter_allowed`. Otherwise,
    the decorator will inject a kwarg `filtered` contains `Query.filter_by(**kwargs)`.
    """

    @wraps(func)
    @secure_sql_error
    def filter_by_allowed(*args, **kwargs):
        included_kwargs = {
            key: kwargs[key] for key in kwargs if key not in args[0].filter_excluded
        }
        if all(key in args[0].filter_allowed for key in included_kwargs):
            kwargs["filtered"] = args[0].query.filter_by(**included_kwargs)
            return func(*args, **kwargs)
        print({key: key in args[0].filter_allowed for key in kwargs})
        return None

    return filter_by_allowed


class QueryMixin:
    filter_allowed = []
    filter_excluded = ["start", "stop"]

    @classmethod
    @secure_sql_error
    @filter_by_allowed_attributes
    def find_by_attributes(cls, **kwargs):
        """
        Find first instance with attributes listed in `kwargs`.
        """
        return kwargs["filtered"].first()

    @classmethod
    @secure_sql_error
    @filter_by_allowed_attributes
    def get_many(cls, start, stop, **kwargs):
        """
        Get list of instances with attributes listed in `kwargs`.
        """
        return kwargs["filtered"].slice(start - 1, stop).all()

    @classmethod
    @secure_sql_error
    @filter_by_allowed_attributes
    def get_size(cls, **kwargs):
        """
        Get total number of instances with attributes listed in `kwargs`.
        """
        print(kwargs["filtered"])
        # return kwargs["filtered"].count()
        return len(kwargs["filtered"].all())


class EditMixin:
    @secure_sql_error
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @secure_sql_error
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
