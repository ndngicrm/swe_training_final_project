from main import db
from main.commons.decorators import filter_by_allowed_attributes, secure_sql_error


class QueryMixin:
    filter_allowed = []
    filter_excluded = ["start", "stop"]

    @classmethod
    @filter_by_allowed_attributes
    @secure_sql_error
    def find_by_attributes(cls, **kwargs):
        """
        Find first instance with attributes listed in `kwargs`.
        """
        return kwargs["filtered"].first()

    @classmethod
    @filter_by_allowed_attributes
    @secure_sql_error
    def get_many(cls, start, stop, **kwargs):
        """
        Get list of instances with attributes listed in `kwargs`.
        """
        return kwargs["filtered"].slice(start - 1, stop).all()

    @classmethod
    @filter_by_allowed_attributes
    @secure_sql_error
    def get_size(cls, **kwargs):
        """
        Get total number of instances with attributes listed in `kwargs`.
        """
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
