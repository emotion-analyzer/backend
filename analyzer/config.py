import os

from dotenv import load_dotenv

load_dotenv(os.getenv(key="APP_ENV", default="test.env"))
load_dotenv(os.getenv(key="DATABASE_ENV", default="../util/database.test.env"))
load_dotenv(os.getenv(key="RABBITMQ_ENV", default="../util/rabbit_mq.test.env"))

class HuggingFace:
    """HuggingFace configuration."""
    MODEL_URL = os.getenv("HUGGINGFACE_MODEL_URL")

class Model:
    """Model configuration."""
    EMOTION_MAPPING = os.getenv("MODEL_EMOTION_MAPPING", "False").lower() == "true"
    MAPPING_FILE = os.getenv("MODEL_MAPPING_FILE")
    THRESHOLD = float(os.getenv("MODEL_EMOTION_THRESHOLD", "0.4"))
    TOP_K = int(os.getenv("MODEL_TOP_K", "1"))

class RabbitMQ:
    """RabbitMQ configuration."""
    USERNAME = os.getenv("RABBITMQ_USERNAME")
    PASSWORD = os.getenv("RABBITMQ_PASSWORD")
    HOST = os.getenv("RABBITMQ_HOST")
    PORT = int(os.getenv("RABBITMQ_PORT"))
    PROCESSING_QUEUE = os.getenv("RABBITMQ_PROCESSING_QUEUE")
    PREFETCH_COUNT = int(os.getenv("RABBITMQ_PREFETCH_COUNT"))

class ElasticSearch:
    """ElasticSearch configuration."""
    ADDRESS = os.getenv("ELASTICSEARCH_ADDRESS", "elasticsearch")
    PORT = os.getenv("ELASTICSEARCH_PORT", "9200")
    # Change to HTTPS later (will need to adjust docker-compose)
    HOST = f"http://{ADDRESS}:{PORT}"

class Config:
    """Represents configuration state in the application.

    Import in your module and access (after setting in the proper .env).
    """
    HUGGING_FACE = HuggingFace
    RABBIT_MQ = RabbitMQ
    MODEL = Model
    ELASTICSEARCH = ElasticSearch

config = Config()
