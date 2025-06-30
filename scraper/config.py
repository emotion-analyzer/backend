import json
import os

from dotenv import load_dotenv

load_dotenv(os.getenv(key="APP_ENV", default="test.env"))
load_dotenv(os.getenv(key="RABBITMQ_ENV", default="../util/rabbit_mq.test.env"))

class Reddit:
    """Reddit scraping configuration."""
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    USER_AGENT = os.getenv("USER_AGENT")
    ES_SUBREDDITS = "+".join(json.loads(os.getenv("ES_SUBREDDITS")))
    RATELIMIT_SECONDS = int(os.getenv("RATELIMIT_SECONDS"))

class Bluesky:
    """Bluesky scraping configuration."""
    BASE_URL = os.getenv("BLUESKY_BASE_URL")
    SEARCH_URL = os.getenv("BLUESKY_SEARCH_URL")

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
    REDDIT = Reddit
    BLUESKY = Bluesky
    RABBIT_MQ = RabbitMQ

config = Config()
