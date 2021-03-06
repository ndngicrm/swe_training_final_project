from datetime import datetime

from sqlalchemy.dialects import mysql

from main import db
from main.models.base import EditMixin, QueryMixin


class ItemModel(db.Model, EditMixin, QueryMixin):
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(mysql.VARCHAR(80), nullable=False, unique=True)
    description = db.Column(mysql.TEXT, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    category = db.relationship("CategoryModel", back_populates="items")

    filter_allowed = ["id", "name", "category_id"]

    def __init__(self, name, description, category_id):
        self.name = name
        self.description = description
        self.category_id = category_id
