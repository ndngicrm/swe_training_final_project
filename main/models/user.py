import secrets
from datetime import datetime
from hashlib import sha256

from sqlalchemy.dialects import mysql

from main import db


class UserModel(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(mysql.VARCHAR(320), nullable=False)
    password = db.Column(mysql.CHAR(64), nullable=False)
    salt = db.Column(mysql.CHAR(32), nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, email, password):
        self.email = email

        self.salt = secrets.token_hex(16)
        self.password = self.__get_password_hash(password, self.salt)

        self.created_time = datetime.now()
        self.updated_time = self.created_time

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def __get_password_hash(cls, password, salt):
        return sha256((password + salt).encode()).hexdigest()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def is_valid_user(cls, email, password):
        user = cls.find_by_email(email)
        if user:
            if cls.__get_password_hash(password, user.salt) == user.password:
                return True
        return False
