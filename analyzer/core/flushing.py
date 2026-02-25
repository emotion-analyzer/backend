import asyncio

from aio_pika import DeliveryMode, Message
from util.codes import POST
from util.queue_middleware import send_message
from util.schemas import Post, QueueMessage

from analyzer.config import config
from analyzer.model.analyze import bulk_analyze_posts


async def periodic_flush(buffer, buffer_lock, results_exchange,
                         available_models, client, logger):
    """Flush buffer in between intervals."""
    while True:
        await asyncio.sleep(config.ELASTICSEARCH.FLUSH_INTERVAL)
        async with buffer_lock:
            await flush_buffer(buffer, results_exchange,
                           available_models, client, logger)

async def flush_buffer(buffer, results_exchange,
                       available_models, client, logger):
    """Process messages in buffer and send responses through RabbitMQ."""
    documents = []
    results = []

    batch_to_process = list(buffer)
    buffer.clear()

    for message in batch_to_process:
        queue_message = QueueMessage.model_validate_json(message.body.decode("utf-8"))
        if queue_message.code == POST:
            post = Post.model_validate_json(message.body.decode("utf-8"))
            documents.append(post)
        else:
            new_message = Message(
                message.body,
                delivery_mode=DeliveryMode.PERSISTENT
            )
            await send_message(results_exchange, new_message,
                               queue_message.query_processor_id, logger)
    analysis_results = await bulk_analyze_posts(available_models, client, documents, logger)
    results.extend(analysis_results)
    for message in results:
        new_message = Message(message.model_dump_json().encode('utf-8'),
                              delivery_mode=DeliveryMode.PERSISTENT)
        await send_message(results_exchange, new_message,
                           message.query_processor_id, logger)
    for item in batch_to_process:
        await item.ack()
