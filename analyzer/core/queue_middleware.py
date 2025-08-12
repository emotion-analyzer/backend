import asyncio
import json

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from analyzer.model.analyze import get_affective_states


async def initiate_connection(config):
    """Initialize the connection to the RabbitMQ server."""
    return await aio_pika.connect_robust(
        host=config.RABBIT_MQ.HOST,
        port=config.RABBIT_MQ.PORT,
        login=config.RABBIT_MQ.USERNAME,
        password=config.RABBIT_MQ.PASSWORD)


def create_callback(tokenizer, model, client):
    """Create callback function."""
    async def process_message(message: AbstractIncomingMessage):
        """Decode message, perform an emotional analysis on it and store the results."""
        post = json.loads(message.body.decode("utf-8"))
        get_affective_states(tokenizer, model, client, post["text"])
    return process_message


async def process_posts(tokenizer, model, client, config) -> None:
    """Connect to RabbitMQ, create channel and queue."""
    connection = await initiate_connection(config)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=config.RABBIT_MQ.PREFETCH_COUNT)
        queue = await channel.declare_queue(config.RABBIT_MQ.PROCESSING_QUEUE)
        await queue.consume(callback=create_callback(tokenizer, model, client),
                            no_ack=True)
        await asyncio.Future()



