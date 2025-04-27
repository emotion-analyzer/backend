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

    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    USER_AGENT = os.getenv("USER_AGENT")


config = Config()
