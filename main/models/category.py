from datetime import datetime

from sqlalchemy.dialects import mysql

from main import db
from main.models.base import EditMixin, QueryMixin


class CategoryModel(db.Model, EditMixin, QueryMixin):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(mysql.VARCHAR(80), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    user = db.relationship("UserModel", back_populates="categories")
    items = db.relationship(
        "ItemModel", back_populates="category", cascade="all, delete-orphan"
    )

    filter_allowed = ["id", "name"]

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id
