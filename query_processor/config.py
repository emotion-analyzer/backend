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

class Fluentd:
    """Fluentd configuration."""
    HOST = os.getenv("FLUENTD_HOST")
    PORT = int(os.getenv("FLUENTD_PORT"))

class Config:
    """Represents configuration state in the application.

    Import in your module and access (after setting in the proper .env).
    """
    RABBIT_MQ = RabbitMQ
    FLUENTD = Fluentd
    TIMEOUT = int(os.getenv("TIMEOUT"))
    SERVICE = "query-processor"
    DEBUG = int(os.getenv("DEBUG","1")) == 1

config = Config()
