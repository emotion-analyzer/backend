from analyzer.config import config
from analyzer.elasticsearch.mappings import analysis_mappings
from analyzer.elasticsearch.settings import analysis_settings
import elasticsearch
from elasticsearch import Elasticsearch


def create_ilm_policy(client):
    """Create and store ILM policy."""
    policy = {
        "policy": {
            "phases": {
                "hot": {
                    "actions": {
                        "rollover": {
                            "max_size": "50GB",
                            "max_age": "30d",
                            "max_docs": 50000000
                        },
                        "set_priority": {
                            "priority": 100
                        }
                    }
                },
                "warm": {
                    "min_age": "30d",
                    "actions": {
                        "shrink": {
                            "number_of_shards": 1
                        },
                        "forcemerge": {
                            "max_num_segments": 1
                        },
                        "set_priority": {
                            "priority": 50
                        }
                    }
                },
                "cold": {
                    "min_age": "90d",
                    "actions": {
                        "set_priority": {
                            "priority": 0
                        }
                    }
                },
                "delete": {
                    "min_age": "365d",
                    "actions": {
                        "delete": {}
                    }
                }
            }
        }
    }
    try:
        client.ilm.get_lifecycle(name="analysis-lifecycle")
    except elasticsearch.NotFoundError:
        client.ilm.put_lifecycle(name="analysis-lifecycle", body=policy)

def initialize_mappings():
    """Initialize ElasticSearch client and define mappings."""
    client = Elasticsearch(config.ELASTICSEARCH.HOST,
                           basic_auth=(config.ELASTICSEARCH.USER,
                                       config.ELASTICSEARCH.PASSWORD),
                           retry_on_timeout=True,
                           max_retries=3)
    create_ilm_policy(client)
    if client.indices.exists(index="analysis-v1"):
        client.indices.delete(index="analysis-v1")
    client.indices.create(
        index="analysis-v1",
        mappings=analysis_mappings,
        settings={
            **analysis_settings,
            "index.lifecycle.name": "analysis-lifecycle",
            "index.lifecycle.rollover_alias": "analysis-current"
        },
        request_timeout=60
    )
    client.indices.put_alias(index="analysis-v1", name="analysis-current")
    client.indices.put_settings(
        index="analysis-current",
        body={
            "index": {
                "search.slowlog.threshold.query.warn": "800ms",
                "search.slowlog.threshold.fetch.warn": "500ms",
                "indexing.slowlog.threshold.index.warn": "2s"
            }
        }
    )

    return client
