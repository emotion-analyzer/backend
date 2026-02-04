import asyncio
import logging

from prometheus_client import start_http_server
from util.logging import initialize_logging

from analyzer.config import config
from analyzer.core.exceptions import FatalConfigurationError
from analyzer.core.queue_middleware import process_posts
from analyzer.elasticsearch.initialization import initialize_es_client
from analyzer.model.initialization import load_models


async def initialize():
    """Initialize database, model and necessary queues."""
    initialize_logging(config.FLUENTD.HOST,
                       config.FLUENTD.PORT,
                       "analyzer")
    logger = logging.getLogger("affect_pulse")
    elasticsearch_client = initialize_es_client()
    available_models = load_models(logger)
    if len(available_models) == 0:
        logger.error("No valid models found after loading attempt.")
        raise FatalConfigurationError("No valid models found after loading attempt."
                                      " Verify configuration and restart node")
    await process_posts(available_models,
                        elasticsearch_client,
                        config, logger)

def main():
    """Main function."""
    start_http_server(8000)
    asyncio.run(initialize())

if __name__ == "__main__":
    main()
