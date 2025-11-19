import json
import os


class General:
    """General scraping configuration."""
    LANGUAGES = json.loads(os.getenv("LANGUAGES"))

class Reddit:
    """Reddit scraping configuration."""
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    USER_AGENT = os.getenv("USER_AGENT")
    ES_SUBREDDITS = "+".join(json.loads(os.getenv("ES_SUBREDDITS")))
    EN_SUBREDDITS = "+".join(json.loads(os.getenv("EN_SUBREDDITS")))
    RATELIMIT_SECONDS = int(os.getenv("RATELIMIT_SECONDS"))
    LIMIT = int(os.getenv("LIMIT"))

class Bluesky:
    """Bluesky scraping configuration."""
    BASE_URL = os.getenv("BLUESKY_BASE_URL")
    SEARCH_URL = os.getenv("BLUESKY_SEARCH_URL")

class Fluentd:
    """Fluentd configuration."""
    HOST = os.getenv("FLUENTD_HOST")
    PORT = int(os.getenv("FLUENTD_PORT"))

class RabbitMQ:
    """RabbitMQ configuration."""
    USERNAME = os.getenv("RABBITMQ_USERNAME")
    PASSWORD = os.getenv("RABBITMQ_PASSWORD")
    FLUENTD = Fluentd
    HOST = os.getenv("RABBITMQ_HOST")
    PORT = int(os.getenv("RABBITMQ_PORT"))
    ANALYSIS_REQUEST_QUEUE = os.getenv("RABBITMQ_ANALYSIS_REQUEST_QUEUE")
    SCRAPING_RESULT_QUEUE = os.getenv("RABBITMQ_SCRAPING_RESULT_QUEUE")

class Config:
    """Represents configuration state in the application.

    Import in your module and access (after setting in the proper .env).
    """
    REDDIT = Reddit
    BLUESKY = Bluesky
    RABBIT_MQ = RabbitMQ
    FLUENTD = Fluentd
    GENERAL = General

config = Config()
