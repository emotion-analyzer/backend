import os

from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv(os.getenv(key="APP_ENV", default="test.env"))
load_dotenv(os.getenv(key="DATABASE_ENV", default="../util/database.test.env"))

class Database:
    """Database configuration. Will generate the URL if one is not provided."""
    URL_ = os.getenv("DATABASE_URL")
    if URL_ is None:
        URL_ = URL.create(drivername=os.getenv("DATABASE_DRIVER"),
                          username=os.getenv("POSTGRES_USER"),
                          password=os.getenv("POSTGRES_PASSWORD"),
                          host=os.getenv("DATABASE_HOST"),
                          port=os.getenv("DATABASE_PORT"),
                          database=os.getenv("POSTGRES_DB"))

class Frontend:
    """Frontend configuration."""
    URL = os.getenv("FRONTEND_URL")

class Mail:
    """Mail configuration."""
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", default="587"))
    ADDRESS = os.getenv("EMAIL_ADDRESS")
    PASSWORD = os.getenv("EMAIL_PASSWORD")

class JSONWebToken:
    """JSONWebToken configuration."""
    KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    EXPIRATION_MINUTES_LOGIN = int(os.getenv("EXPIRATION_MIN_LOGIN"))
    EXPIRATION_MINUTES_PW_RESET = int(os.getenv("EXPIRATION_MIN_PASSWORD_RESET"))

class Kong:
    """Kong gateway configuration."""
    KEY = os.getenv("KONG_KEY")

class Minio:
    """Minio configuration."""
    ADDRESS = os.getenv("MINIO_ADDRESS")
    HOST = os.getenv("MINIO_HOST")
    PORT = os.getenv("MINIO_PORT")
    USER = os.getenv("MINIO_USER")
    PASSWORD = os.getenv("MINIO_PASSWORD")
    BUCKET = os.getenv("MINIO_BUCKET")

class Config:
    """Represents configuration state in the application.

    Import in your module and access (after setting in the proper .env).
    """
    DATABASE = Database
    FRONTEND = Frontend
    MAIL = Mail
    KONG = Kong
    JWT = JSONWebToken
    MINIO = Minio
    TESTING = bool(os.getenv("TESTING", default="False"))


config = Config()
