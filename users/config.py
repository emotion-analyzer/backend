import os

from dotenv import load_dotenv

# This could be fancier/more structured

if os.getenv("TESTING"):
    load_dotenv(".env.test")
else:
    # This should load the production env
    load_dotenv(".env.test")


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
