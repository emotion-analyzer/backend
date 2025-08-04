import aio_pika
from aio_pika import ExchangeType


async def initiate_connection(config):
    """Initialize the connection to the RabbitMQ server."""
    connection = await aio_pika.connect_robust(
        host=config.RABBIT_MQ.HOST,
        port=config.RABBIT_MQ.PORT,
        login=config.RABBIT_MQ.USERNAME,
        password=config.RABBIT_MQ.PASSWORD)
    return await connection.channel()

async def initialize_queues(channel, config):
    await channel.set_qos(prefetch_count=config.RABBIT_MQ.PREFETCH_COUNT)
    posts_queue = await channel.declare_queue("scrape_requests")
    topic_logs_exchange = await channel.declare_exchange("results_exchange", ExchangeType.TOPIC)
    return posts_queue, topic_logs_exchange