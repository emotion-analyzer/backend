import asyncio

from aio_pika.abc import AbstractIncomingMessage
from util.queue_middleware import (
    configure,
    declare_queue,
    initialize_exchange,
    initiate_connection,
)

from analyzer.config import config
from analyzer.core.flushing import flush_buffer, periodic_flush

def create_callback(xch, available_models, buffer, lock, client, logger):
    """Create callback function."""
    async def process_message(message: AbstractIncomingMessage):
        """Decode message, perform an emotional analysis on it and store the results."""
        async with lock:
            buffer.append(message)
            if len(buffer) >= config.ELASTICSEARCH.BATCH_SIZE:
                await flush_buffer(buffer, xch, available_models,
                                   client, logger)
    return process_message


async def process_posts(available_models, client, config, logger) -> None:
    """Connect to RabbitMQ, create channel and queue."""
    connection = await initiate_connection(config)
    buffer = []
    buffer_lock = asyncio.Lock()
    async with connection:
        channel = await connection.channel()
        await configure(channel, config.RABBIT_MQ.PREFETCH_COUNT)
        queue = await declare_queue(channel,
                                    config.RABBIT_MQ.SCRAPING_RESULT_QUEUE,
                                    logger)
        xch = await initialize_exchange(channel,
                                        config.RABBIT_MQ.RESULT_EXCHANGE,
                                        logger)
        flush_task = asyncio.create_task(periodic_flush(buffer, buffer_lock, xch,
                                           available_models, client, logger))
        await queue.consume(callback=create_callback(xch, available_models, buffer,
                                                     buffer_lock, client, logger),
                            no_ack=False)
        await flush_task
        await asyncio.Future()
