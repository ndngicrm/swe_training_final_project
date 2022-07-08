from datetime import datetime

from sqlalchemy.dialects import mysql

from main import db
from main.models.base import BaseModel, PaginationModel


class ItemModel(db.Model, BaseModel, PaginationModel):
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(mysql.VARCHAR(80), nullable=False, unique=True)
    description = db.Column(mysql.TEXT, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    category = db.relationship("CategoryModel", back_populates="items")

    def __init__(self, name, description, category_id):
        self.name = name
        self.description = description
        self.category_id = category_id

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_many_in_category(cls, category_id, start, stop):
        return cls.query.filter_by(category_id=category_id).slice(start - 1, stop).all()

    @classmethod
    def get_size_in_category(cls, category_id):
        return cls.query.filter_by(category_id=category_id).count()
