import logging

from es_initializer.config import config
from es_initializer.v1.mappings import analysis_mappings
from es_initializer.v1.settings import analysis_settings
import elasticsearch
from elasticsearch import Elasticsearch

from util.logging import initialize_logging


def setup_snapshots(client, repository_path="/usr/share/elasticsearch/snapshots"):
    """Set up automated snapshots."""
    repo_name = "analysis_backups"

    client.snapshot.create_repository(
        name=repo_name,
        body={
            "type": "fs",
            "settings": {
                "location": repository_path,
                "compress": True
            }
        }
    )
    policy_name = "daily_snapshots"
    client.slm.put_lifecycle(
        policy_id=policy_name,
        body={
            "schedule": "0 0 2 * * ?",
            "name": "<analysis-snapshot-{now/d}>",
            "repository": repo_name,
            "config": {
                "indices": ["analysis-*"],
                "include_global_state": False
            },
            "retention": {
                "expire_after": "30d",  # Keep for 30 days
                "min_count": 5,  # Keep at least 5
                "max_count": 50  # Keep max 50
            }
        }
    )


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

def create_basic_user(client):
    role_name = "analyzer"
    role_body = {
        "indices": [
            {
                "names": ["analysis-*"],
                "privileges": ["read", "write", "create_index"]
            }
        ]
    }

    client.security.put_role(name=role_name, body=role_body)

    username = "analyzer"
    password = "analyzer"

    client.security.put_user(
        username=username,
        password=password,
        roles=["analyzer"]
    )

def setup_elasticsearch(logger):
    """Initialize ElasticSearch client and define mappings."""
    client = Elasticsearch(config.ELASTICSEARCH.HOST,
                           basic_auth=(config.ELASTICSEARCH.USER,
                                       config.ELASTICSEARCH.PASSWORD),
                           retry_on_timeout=True,
                           max_retries=3)
    version = config.INDEX.VERSION
    # Faltaria crear el usuario basico para el analizador
    create_ilm_policy(client)
    if client.indices.exists(index=f"analysis-{version}"):
        client.indices.delete(index=f"analysis-{version}")
    client.options(request_timeout=60).indices.create(
        index=f"analysis-{version}",
        mappings=analysis_mappings,
        settings={
            **analysis_settings,
            "index.lifecycle.name": "analysis-lifecycle",
            "index.lifecycle.rollover_alias": "analysis-current",
            "index.search.slowlog.threshold.query.warn": "800ms",
            "index.search.slowlog.threshold.fetch.warn": "500ms",
            "index.indexing.slowlog.threshold.index.warn": "2s",
        },
    )
    client.indices.put_alias(index=f"analysis-{version}", name="analysis-current")
    #setup_snapshots(client)
    create_basic_user(client)
    logger.info("Finished Elasticsearch configuration")

if __name__ == "__main__":
    initialize_logging(config.FLUENTD.HOST,
                       config.FLUENTD.PORT,
                       "query_processor")
    logger = logging.getLogger("affect_pulse")
    setup_elasticsearch(logger)