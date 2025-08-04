import asyncio

import aio_pika
from aio_pika import Message
from aio_pika.abc import AbstractIncomingMessage, ExchangeType, DeliveryMode

from analyzer.model.analyze import analyze_post
from analyzer.core.schemas import Post, QueueMessage
from analyzer.model.codes import POST


async def initiate_connection(config):
    """Initialize the connection to the RabbitMQ server."""
    return await aio_pika.connect_robust(
        host=config.RABBIT_MQ.HOST,
        port=config.RABBIT_MQ.PORT,
        login=config.RABBIT_MQ.USERNAME,
        password=config.RABBIT_MQ.PASSWORD)


def create_callback(tokenizer, model, client, topic_logs_exchange):
    """Create callback function."""
    async def process_message(message: AbstractIncomingMessage):
        """Decode message, perform an emotional analysis on it and store the results."""
        queue_message = QueueMessage.model_validate_json(message.body.decode("utf-8"))
        if queue_message.code == POST:
            post = Post.model_validate_json(message.body.decode("utf-8"))
            analyzed_post = analyze_post(tokenizer, model, client, post)
            message = Message(analyzed_post.model_dump_json().encode('utf-8'), delivery_mode=DeliveryMode.PERSISTENT)
        else:
            message = Message(queue_message.model_dump_json().encode('utf-8'), delivery_mode=DeliveryMode.PERSISTENT)
        await topic_logs_exchange.publish(message, routing_key=queue_message.query_processor_id)
    return process_message


async def process_posts(tokenizer, model, client, config) -> None:
    """Connect to RabbitMQ, create channel and queue."""
    connection = await initiate_connection(config)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=config.RABBIT_MQ.PREFETCH_COUNT)
        queue = await channel.declare_queue(config.RABBIT_MQ.PROCESSING_QUEUE)
        topic_logs_exchange = await channel.declare_exchange("results_exchange", ExchangeType.TOPIC)
        await queue.consume(callback=create_callback(tokenizer, model, client, topic_logs_exchange), no_ack=True)
        await asyncio.Future()



