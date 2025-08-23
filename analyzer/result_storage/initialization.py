from elasticsearch import Elasticsearch

from analyzer.config import config
from analyzer.result_storage.mappings import analysis_mappings


def initialize_mappings():
    """Initialize ElasticSearch client and define mappings."""
    client = Elasticsearch(config.ELASTICSEARCH.HOST)
    if client.indices.exists(index="analysis_index"):
        client.indices.delete(index="analysis_index")
    client.indices.create(index="analysis_index",
                          mappings=analysis_mappings,
                          request_timeout=60)
    return client
