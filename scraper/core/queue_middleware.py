
import aio_pika
from aio_pika.abc import AbstractRobustChannel


async def initiate_connection(config):
    """Initialize the connection to the RabbitMQ server."""
    return await aio_pika.connect_robust(
        host=config.RABBIT_MQ.HOST,
        port=config.RABBIT_MQ.PORT,
        login=config.RABBIT_MQ.USERNAME,
        password=config.RABBIT_MQ.PASSWORD)


async def initialize_channel(config)-> AbstractRobustChannel:
    """Connect to RabbitMQ, initialize with the queue and return the channel."""
    connection = await initiate_connection(config)
    await connection.connect()
    channel = await connection.channel()
    await channel.declare_queue(config.RABBIT_MQ.PROCESSING_QUEUE)
    return channel


async def send_message(message, channel, config) -> None:
    """Return relevant social media posts according to query parameters."""
    await channel.default_exchange.publish(message,
                                           routing_key=config.RABBIT_MQ.PROCESSING_QUEUE)
