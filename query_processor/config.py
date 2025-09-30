import os


class RabbitMQ:
    """RabbitMQ configuration."""
    USERNAME = os.getenv("RABBITMQ_USERNAME")
    PASSWORD = os.getenv("RABBITMQ_PASSWORD")
    HOST = os.getenv("RABBITMQ_HOST")
    PORT = int(os.getenv("RABBITMQ_PORT"))
    PREFETCH_COUNT = int(os.getenv("RABBITMQ_PREFETCH_COUNT"))
    ANALYSIS_REQUEST_QUEUE = os.getenv("RABBITMQ_ANALYSIS_REQUEST_QUEUE")
    RESULT_EXCHANGE = os.getenv("RABBITMQ_ANALYSIS_RESULT_EXCHANGE")
    ANALYSIS_RESULT_QUEUE = os.getenv("RABBITMQ_ANALYSIS_RESULT_QUEUE")


class FastText:
    """FastText configuration."""
    PATH = os.getenv("FASTTEXT_PATH")
    THRESHOLD = os.getenv("FASTTEXT_THRESHOLD")

class Config:
    """Represents configuration state in the application.

    Import in your module and access (after setting in the proper .env).
    """
    RABBIT_MQ = RabbitMQ
    FASTTEXT = FastText
    TIMEOUT = int(os.getenv("TIMEOUT"))

config = Config()
