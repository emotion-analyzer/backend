import asyncio

from aio_pika import Message
from aio_pika.abc import AbstractIncomingMessage, DeliveryMode
from util.codes import POST, POST_ANALYSIS_RESULT
from util.queue_middleware import (
    configure,
    declare_queue,
    initialize_exchange,
    initiate_connection,
    send_message,
)
from util.schemas import Post, QueueMessage

from analyzer.model.analyze import analyze_post

documents = []

def create_callback(available_models, client, results_exchange, logger):
    """Create callback function."""
    async def process_message(message: AbstractIncomingMessage):
        """Decode message, perform an emotional analysis on it and store the results."""
        queue_message = QueueMessage.model_validate_json(message.body.decode("utf-8"))
        try:
            if queue_message.code == POST:
                post = Post.model_validate_json(message.body.decode("utf-8"))
                # documents.append(post)
                # bulk_analyze_posts(available_models, client, post, logger)
                analyzed_post = analyze_post(available_models, client, post, logger)
                if analyzed_post is None:
                    return
                analyzed_post.code = POST_ANALYSIS_RESULT
                new_message = Message(analyzed_post.model_dump_json().encode('utf-8'),
                                  delivery_mode=DeliveryMode.PERSISTENT)
            else:
                new_message = Message(message.body, delivery_mode=DeliveryMode.PERSISTENT)
            await send_message(results_exchange, new_message,
                               queue_message.query_processor_id, logger)
        finally:
            await message.ack()
    return process_message


async def process_posts(available_models, client, config, logger) -> None:
    """Connect to RabbitMQ, create channel and queue."""
    connection = await initiate_connection(config)
    async with connection:
        channel = await connection.channel()
        await configure(channel, config.RABBIT_MQ.PREFETCH_COUNT)
        queue = await declare_queue(channel,
                                    config.RABBIT_MQ.SCRAPING_RESULT_QUEUE,
                                    logger)
        xch = await initialize_exchange(channel,
                                        config.RABBIT_MQ.RESULT_EXCHANGE,
                                        logger)
        await queue.consume(callback=create_callback(available_models,
                                                     client,
                                                     xch,
                                                     logger),
                            no_ack=False)
        await asyncio.Future()
