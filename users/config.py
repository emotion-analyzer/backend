import os

from dotenv import load_dotenv

load_dotenv(os.getenv(key="APP_ENV", default="test.env"))

class Config:
    """Represents configuration state in the application.

    Import in your module and access (after setting in the proper .env).
    """

    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    KONG_KEY = os.getenv("KONG_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"


config = Config()
