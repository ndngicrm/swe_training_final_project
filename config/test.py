from .local import Config as _Config


class Config(_Config):
    TESTING = True

    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://root:123456789@localhost:3306/catalog_test"
    )
    SECRET_KEY = "test"
