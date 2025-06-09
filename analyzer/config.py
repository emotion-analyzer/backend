import os

from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv(os.getenv(key="APP_ENV", default="test.env"))
load_dotenv(os.getenv(key="DATABASE_ENV", default="../util/database.test.env"))
load_dotenv(os.getenv(key="RABBITMQ_ENV", default="../util/rabbit_mq.test.env"))

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

class HuggingFace:
    """HuggingFace configuration."""
    MODEL_URL = os.getenv("HUGGINGFACE_MODEL_URL")

class Model:
    """Model configuration."""
    EMOTION_MAPPING = os.getenv("MODEL_EMOTION_MAPPING", "False").lower() == "true"
    MAPPING_FILE = os.getenv("MODEL_MAPPING_FILE")

class RabbitMQ:
    """RabbitMQ configuration."""
    USERNAME = os.getenv("RABBITMQ_USERNAME")
    PASSWORD = os.getenv("RABBITMQ_PASSWORD")
    HOST = os.getenv("RABBITMQ_HOST")
    PORT = int(os.getenv("RABBITMQ_PORT"))
    PROCESSING_QUEUE = os.getenv("RABBITMQ_PROCESSING_QUEUE")
    PREFETCH_COUNT = int(os.getenv("RABBITMQ_PREFETCH_COUNT"))

class Config:
    """Represents configuration state in the application.

    Import in your module and access (after setting in the proper .env).
    """
    HUGGING_FACE = HuggingFace
    DATABASE = Database
    RABBIT_MQ = RabbitMQ
    MODEL = Model

config = Config()
