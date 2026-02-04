from analyzer.config import config
from elasticsearch import Elasticsearch

def initialize_es_client():
    """Initialize ElasticSearch client and define mappings."""
    client = Elasticsearch(config.ELASTICSEARCH.HOST,
                           basic_auth=(config.ELASTICSEARCH.USER,
                                       config.ELASTICSEARCH.PASSWORD),
                           retry_on_timeout=True,
                           max_retries=3)
    return client
