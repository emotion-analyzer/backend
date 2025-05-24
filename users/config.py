import os

from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv(os.getenv(key="APP_ENV", default="prod.env"))

class Config:
    """Represents configuration state in the application.

    Import in your module and access (after setting in the proper .env).
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL is None:
        DATABASE_URL = URL.create(drivername=os.getenv("DATABASE_DRIVER"),
                                 username=os.getenv("POSTGRES_USER"),
                                 password=os.getenv("POSTGRES_PASSWORD"),
                                 host=os.getenv("DATABASE_HOST"),
                                 port=os.getenv("DATABASE_PORT"),
                                 database=os.getenv("POSTGRES_DB"))
    EXPIRATION_MINUTES_LOGIN = int(os.getenv("EXPIRATION_MIN_LOGIN"))
    EXPIRATION_MINUTES_PW_RESET = int(os.getenv("EXPIRATION_MIN_PASSWORD_RESET"))
    SECRET_KEY = os.getenv("SECRET_KEY")
    KONG_KEY = os.getenv("KONG_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", default="587"))
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


config = Config()
