import asyncio

from aio_pika import Message
from aio_pika.abc import AbstractIncomingMessage, DeliveryMode

from scraper.config import config
from scraper.core.bluesky import BlueskyScraper
from scraper.core.queue_middleware import initialize_channel, send_message
from scraper.core.reddit import RedditScraper
from scraper.core.schemas import PostRequest, QueueMessage
from scraper.exceptions.exceptions import ScraperError
from scraper.messages.codes import EOF, NONEXISTENT_SCRAPER, SCRAPER_ERROR


def create_callback(available_scrapers, channel):
    """Create callback function."""
    async def process_scrape_request(message: AbstractIncomingMessage):
        """Decode message, perform an emotional analysis on it and store the results."""
        query = PostRequest.model_validate_json(message.body.decode("utf-8"))
        try:
            code = EOF
            scrapers = []
            if "all" in query.analysis_parameters.platform:
                scrapers = available_scrapers.values()
            else:
                for platform in query.analysis_parameters.platform:
                    scraper = available_scrapers.get(platform)
                    if scraper is None:
                        code = NONEXISTENT_SCRAPER
                    scrapers.append(scraper)
            for scraper in scrapers:
                await scraper.query(query.analysis_parameters, query.query_processor_id)
        except ScraperError as e:
            code = SCRAPER_ERROR
        await message.ack()
        body = QueueMessage(query_processor_id=query.query_processor_id, code=code)
        message = Message(body.model_dump_json().encode('utf-8'),
                          delivery_mode=DeliveryMode.NOT_PERSISTENT)
        await send_message(message, channel, config)
    return process_scrape_request

async def initialize_scraper():
    channel = await initialize_channel(config)
    scrapers = {"reddit": RedditScraper("reddit", channel),
                "bluesky": BlueskyScraper("bluesky", channel)}
    await channel.declare_queue(config.RABBIT_MQ.PROCESSING_QUEUE)
    scrape_requests_queue = await channel.declare_queue("scrape_requests")
    await scrape_requests_queue.consume(callback=create_callback(scrapers, channel), no_ack=False)
    await asyncio.Future()

def main():
    asyncio.run(initialize_scraper())

if __name__ == "__main__":
    main()