import os


class HuggingFace:
    """HuggingFace configuration."""
    REPO = os.getenv("HUGGINGFACE_REPO")
    MODELS = os.getenv("HUGGINGFACE_MODELS")

class Model:
    """Model configuration."""
    CLASSIFICATION_THRESHOLD = float(os.getenv("CLASSIFICATION_MODEL_THRESHOLD", "0.30"))
    GENERATIVE_THRESHOLD = float(os.getenv("GENERATIVE_MODEL_THRESHOLD", "0.30"))

class RabbitMQ:
    """RabbitMQ configuration."""
    USERNAME = os.getenv("RABBITMQ_USERNAME")
    PASSWORD = os.getenv("RABBITMQ_PASSWORD")
    HOST = os.getenv("RABBITMQ_HOST")
    PORT = int(os.getenv("RABBITMQ_PORT"))
    PREFETCH_COUNT = int(os.getenv("RABBITMQ_PREFETCH_COUNT"))
    SCRAPING_RESULT_QUEUE = os.getenv("RABBITMQ_SCRAPING_RESULT_QUEUE")
    RESULT_EXCHANGE = os.getenv("RABBITMQ_ANALYSIS_RESULT_EXCHANGE")

class Fluentd:
    """Fluentd configuration."""
    HOST = os.getenv("FLUENTD_HOST")
    PORT = int(os.getenv("FLUENTD_PORT"))

class ElasticSearch:
    """ElasticSearch configuration."""
    ADDRESS = os.getenv("ELASTICSEARCH_ADDRESS", "elasticsearch")
    PORT = os.getenv("ELASTICSEARCH_PORT", "9200")
    USER = os.getenv("ELASTICSEARCH_USER")
    PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")
    # Change to HTTPS later (will need to adjust docker-compose)
    HOST = f"http://{ADDRESS}:{PORT}"
    FLUSH_INTERVAL = float(os.getenv("ELASTICSEARCH_FLUSH_INTERVAL", "0.5"))
    BATCH_SIZE = int(os.getenv("ELASTICSEARCH_BATCH_SIZE", "500"))

class Config:
    """Represents configuration state in the application.

    Import in your module and access (after setting in the proper .env).
    """
    HUGGING_FACE = HuggingFace
    RABBIT_MQ = RabbitMQ
    MODEL = Model
    ELASTICSEARCH = ElasticSearch
    FLUENTD = Fluentd

config = Config()
