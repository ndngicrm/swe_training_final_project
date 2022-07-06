import logging


class BaseConfig:
    LOGGING_LEVEL = logging.INFO

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456789@localhost:3306/catalog"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
