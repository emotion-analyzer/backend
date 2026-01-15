from analyzer.config import config
from analyzer.elasticsearch.mappings import analysis_mappings
from analyzer.elasticsearch.settings import analysis_settings
from elasticsearch import Elasticsearch


def initialize_mappings():
    """Initialize ElasticSearch client and define mappings."""
    client = Elasticsearch(config.ELASTICSEARCH.HOST,
                           basic_auth=(config.ELASTICSEARCH.USER,
                                       config.ELASTICSEARCH.PASSWORD),
                           retry_on_timeout=True,
                           max_retries=3)
    if client.indices.exists(index="analysis-v1"):
        client.indices.delete(index="analysis-v1")
    client.indices.create(index="analysis-v1",
                          mappings=analysis_mappings,
                          settings=analysis_settings,
                          request_timeout=60)
    client.indices.put_alias(index="analysis-v1", name="analysis-current")
    return client
