import asyncio

from aio_pika import Message
from aio_pika.abc import AbstractIncomingMessage, DeliveryMode
from util.codes import EOF
from util.schemas import AnalysisRequest, EOFPosts

from scraper.config import config
from scraper.core.bluesky import BlueskyScraper
from scraper.core.queue_middleware import initialize_channel, send_message
from scraper.core.reddit import RedditScraper


def create_callback(available_scrapers, channel):
    """Create callback function."""
    async def process_scrape_request(message: AbstractIncomingMessage):
        """Scrape social media according to parameters, then queue the results."""
        query = AnalysisRequest.model_validate_json(message.body.decode("utf-8"))
        total = 0
        scrapers = []
        if "all" in query.parameters.platform:
            scrapers = available_scrapers.values()
        else:
            for platform in query.parameters.platform:
                scraper = available_scrapers.get(platform)
                if scraper is None:
                    continue
                scrapers.append(scraper)
        for scraper in scrapers:
            messages_sent = await scraper.query(query)
            total += messages_sent
        await message.ack()
        body = EOFPosts(query_processor_id=query.query_processor_id,
                        code=EOF,
                        total=total)
        message = Message(body.model_dump_json().encode('utf-8'),
                          delivery_mode=DeliveryMode.PERSISTENT)
        await send_message(message, channel, config)
    return process_scrape_request

async def initialize_scraper():
    """Initialize scrapers and necessary queues."""
    channel = await initialize_channel(config)
    scrapers = {"reddit": RedditScraper("reddit", channel),
                "bluesky": BlueskyScraper("bluesky", channel)}
    await channel.declare_queue(config.RABBIT_MQ.SCRAPING_RESULT_QUEUE, durable=True)
    scrape_queue = await channel.declare_queue(config.RABBIT_MQ.ANALYSIS_REQUEST_QUEUE,
                                                        durable=True)
    await scrape_queue.consume(callback=create_callback(scrapers, channel),
                                        no_ack=False)
    await asyncio.Future()

def main():
    """Main function."""
    asyncio.run(initialize_scraper())

if __name__ == "__main__":
    main()
