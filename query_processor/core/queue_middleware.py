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
    """Initialize required queue(s)."""
    await channel.set_qos(prefetch_count=config.RABBIT_MQ.PREFETCH_COUNT)
    posts_queue = await channel.declare_queue(config.RABBIT_MQ.ANALYSIS_REQUEST_QUEUE,
                                              durable=True)
    return posts_queue

async def initialize_exchange(channel, config):
    """Initialize required exchange(s)."""
    results_exchange = await channel.declare_exchange(config.RABBIT_MQ.RESULT_EXCHANGE,
                                                      ExchangeType.TOPIC)
    return results_exchange
