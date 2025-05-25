import os

from dotenv import load_dotenv

load_dotenv(os.getenv(key="APP_ENV", default="test.env"))

class HuggingFace:
    """HuggingFace configuration."""
    MODEL_URL = os.getenv("HUGGINGFACE_MODEL_URL")

class Config:
    """Represents configuration state in the application.

    Import in your module and access (after setting in the proper .env).
    """
    HUGGING_FACE = HuggingFace

config = Config()
