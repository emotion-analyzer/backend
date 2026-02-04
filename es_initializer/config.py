import os


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

class Index:
    """Index configuration."""
    VERSION = os.getenv("INDEX_VERSION")

class Config:
    """Represents configuration state in the application.

    Import in your module and access (after setting in the proper .env).
    """
    ELASTICSEARCH = ElasticSearch
    FLUENTD = Fluentd
    INDEX = Index

config = Config()
