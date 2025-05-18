import os

from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv(os.getenv(key="APP_ENV", default=".env"))

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
    SECRET_KEY = os.getenv("SECRET_KEY")
    KONG_KEY = os.getenv("KONG_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"


config = Config()
