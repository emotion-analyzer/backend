import os

from dotenv import load_dotenv

load_dotenv(os.getenv(key="APP_ENV", default="test.env"))
load_dotenv(os.getenv(key="RABBITMQ_ENV", default="../util/rabbit_mq.test.env"))

class Mapping:
    """Emotion mapping configuration."""
    APPLY = os.getenv("MODEL_EMOTION_MAPPING", "False").lower() == "true"
    FILE = os.getenv("MODEL_MAPPING_FILE")

class RabbitMQ:
    """RabbitMQ configuration."""
    USERNAME = os.getenv("RABBITMQ_USERNAME")
    PASSWORD = os.getenv("RABBITMQ_PASSWORD")
    HOST = os.getenv("RABBITMQ_HOST")
    PORT = int(os.getenv("RABBITMQ_PORT"))
    PREFETCH_COUNT = int(os.getenv("RABBITMQ_PREFETCH_COUNT"))
    ANALYSIS_REQUEST_QUEUE = os.getenv("RABBITMQ_ANALYSIS_REQUEST_QUEUE")
    ANALYSIS_RESULT_EXCHANGE = os.getenv("RABBITMQ_ANALYSIS_RESULT_EXCHANGE")
    ANALYSIS_RESULT_QUEUE = os.getenv("RABBITMQ_ANALYSIS_RESULT_QUEUE")

class Config:
    """Represents configuration state in the application.

    Import in your module and access (after setting in the proper .env).
    """
    RABBIT_MQ = RabbitMQ
    MAPPING = Mapping

config = Config()
