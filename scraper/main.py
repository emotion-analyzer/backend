import asyncio
from datetime import UTC
import logging

from aio_pika import Message
from aio_pika.abc import AbstractIncomingMessage, DeliveryMode
from prometheus_client import start_http_server
from util.codes import EOF
from util.logging import initialize_logging
from util.queue_middleware import (
    configure,
    declare_queue,
    initiate_connection,
    send_message,
)
from util.schemas import AnalysisRequest, EndOfPosts

from scraper.config import config
from scraper.core.bluesky_scraper import BlueskyScraper
from scraper.core.reddit_scraper import RedditScraper


def create_callback(available_scrapers, channel, logger):
    """Create callback function."""
    async def process_scrape_request(message: AbstractIncomingMessage):
        """Scrape social media according to parameters, then queue the results."""
        query = AnalysisRequest.model_validate_json(message.body.decode("utf-8"))
        query.parameters.from_ = query.parameters.from_.replace(tzinfo=UTC)
        query.parameters.to = query.parameters.to.replace(tzinfo=UTC)
        total = 0
        scrapers = []
        if "all" in query.parameters.platform:
            scrapers = available_scrapers.values()
        else:
            for platform in query.parameters.platform:
                scraper = available_scrapers.get(platform)
                if scraper is None:
                    logger.warning(f"Scraper {platform} not available, skipping...")
                    continue
                scrapers.append(scraper)
        for scraper in scrapers:
            messages_sent = await scraper.query(query)
            total += messages_sent
        await message.ack()
        body = EndOfPosts(query_processor_id=query.query_processor_id,
                          code=EOF,
                          total=total)
        message = Message(body.model_dump_json().encode('utf-8'),
                          delivery_mode=DeliveryMode.PERSISTENT)
        await send_message(channel.default_exchange, message,
                           config.RABBIT_MQ.SCRAPING_RESULT_QUEUE,
                           logger)
    return process_scrape_request

async def initialize_scraper():
    """Initialize scrapers and necessary queues."""
    initialize_logging(config.FLUENTD.HOST,
                       config.FLUENTD.PORT,
                       "scraper")
    logger = logging.getLogger("affect_pulse")
    connection = await initiate_connection(config)
    channel = await connection.channel()
    await configure(channel, config.RABBIT_MQ.PREFETCH_COUNT)
    scrapers = {"reddit": RedditScraper("Reddit", channel,
                                        config.GENERAL.LANGUAGES, logger),
                "bluesky": BlueskyScraper("Bluesky", channel,
                                          config.GENERAL.LANGUAGES, logger)}
    await declare_queue(channel, config.RABBIT_MQ.SCRAPING_RESULT_QUEUE, logger)
    scrape_requests_queue = await declare_queue(channel,
                                                config.RABBIT_MQ.ANALYSIS_REQUEST_QUEUE,
                                                logger)
    logger.info("Service initialized awaiting scrap requests...")
    await scrape_requests_queue.consume(callback=create_callback(scrapers,
                                                                 channel, logger),
                                        no_ack=False)
    await asyncio.Future()

def main():
    """Main function."""
    start_http_server(8000)
    asyncio.run(initialize_scraper())

if __name__ == "__main__":
    main()
