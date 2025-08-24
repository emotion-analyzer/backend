import asyncio

import aio_pika
from aio_pika import Message
from aio_pika.abc import AbstractIncomingMessage, DeliveryMode, ExchangeType
from util.codes import POST, POST_ANALYSIS_RESULT
from util.schemas import Post, QueueMessage

from analyzer.model.analyze import analyze_post


async def initiate_connection(config):
    """Initialize the connection to the RabbitMQ server."""
    return await aio_pika.connect_robust(
        host=config.RABBIT_MQ.HOST,
        port=config.RABBIT_MQ.PORT,
        login=config.RABBIT_MQ.USERNAME,
        password=config.RABBIT_MQ.PASSWORD)


def create_callback(available_models, client, results_exchange):
    """Create callback function."""
    async def process_message(message: AbstractIncomingMessage):
        """Decode message, perform an emotional analysis on it and store the results."""
        queue_message = QueueMessage.model_validate_json(message.body.decode("utf-8"))
        if queue_message.code == POST:
            post = Post.model_validate_json(message.body.decode("utf-8"))
            analyzed_post = analyze_post(available_models, client, post)
            analyzed_post.code = POST_ANALYSIS_RESULT
            new_message = Message(analyzed_post.model_dump_json().encode('utf-8'),
                              delivery_mode=DeliveryMode.PERSISTENT)
        else:
            new_message = Message(message.body, delivery_mode=DeliveryMode.PERSISTENT)
        await results_exchange.publish(new_message,
                                       routing_key=queue_message.query_processor_id)
        await message.ack()
    return process_message


async def process_posts(available_models, client, config) -> None:
    """Connect to RabbitMQ, create channel and queue."""
    connection = await initiate_connection(config)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=config.RABBIT_MQ.PREFETCH_COUNT)
        queue = await channel.declare_queue(config.RABBIT_MQ.SCRAPING_RESULT_QUEUE,
                                            durable=True)
        xch = await channel.declare_exchange(config.RABBIT_MQ.ANALYSIS_RESULT_EXCHANGE,
                                                             ExchangeType.TOPIC)
        await queue.consume(callback=create_callback(available_models, client, xch),
                            no_ack=False)
        await asyncio.Future()



