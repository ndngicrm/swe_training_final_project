from main import db


class BaseModel:
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()


class PaginationModel:
    @classmethod
    def get_many(cls, start, stop):
        return cls.query.slice(start - 1, stop).all()

    @classmethod
    def get_size(cls):
        return cls.query.count()
