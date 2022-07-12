import secrets
from datetime import datetime
from hashlib import sha256

from sqlalchemy.dialects import mysql

from main import db
from main.models.base import EditMixin, QueryMixin


class UserModel(db.Model, EditMixin, QueryMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(mysql.VARCHAR(320), nullable=False, unique=True)
    password = db.Column(mysql.CHAR(64), nullable=False)
    salt = db.Column(mysql.CHAR(32), nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    categories = db.relationship("CategoryModel", back_populates="user")

    filter_allowed = ["id", "email"]

    def __init__(self, email, password):
        self.email = email

        self.salt = secrets.token_hex(16)
        self.password = self.__get_password_hash(password, self.salt)

        self.created_time = datetime.now()
        self.updated_time = self.created_time

    @classmethod
    def __get_password_hash(cls, password, salt):
        return sha256((password + salt).encode()).hexdigest()

    @classmethod
    def is_valid_user(cls, email, password):
        user = cls.find_by_attributes(email=email)
        if user:
            if cls.__get_password_hash(password, user.salt) == user.password:
                return True
        return False
