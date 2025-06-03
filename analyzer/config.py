import os

from dotenv import load_dotenv

load_dotenv(os.getenv(key="APP_ENV", default="test.env"))
load_dotenv(os.getenv(key="RABBITMQ_ENV", default="../util/rabbit_mq.test.env"))

class HuggingFace:
    """HuggingFace configuration."""
    MODEL_URL = os.getenv("HUGGINGFACE_MODEL_URL")

class Model:
    """Model configuration."""
    MAPPING = os.getenv("HUGGINGFACE_MAPPING")

class RabbitMQ:
    """RabbitMQ configuration."""
    USERNAME = os.getenv("RABBITMQ_USERNAME")
    PASSWORD = os.getenv("RABBITMQ_PASSWORD")
    HOST = os.getenv("RABBITMQ_HOST")
    PORT = int(os.getenv("RABBITMQ_PORT"))
    PROCESSING_QUEUE = os.getenv("RABBITMQ_PROCESSING_QUEUE")

class Config:
    """Represents configuration state in the application.

    Import in your module and access (after setting in the proper .env).
    """
    HUGGING_FACE = HuggingFace
    RABBIT_MQ = RabbitMQ

config = Config()
