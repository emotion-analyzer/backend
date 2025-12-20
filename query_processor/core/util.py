import asyncio

from aio_pika import Message
from aio_pika.exceptions import (ChannelClosed, AMQPConnectionError,
                                 ConnectionClosed)


from util.codes import ANALYSIS_REQUEST, EOF, POST_ANALYSIS_RESULT
from util.queue_middleware import declare_queue, send_message
from util.schemas import (
    AnalysisRequest,
    EndOfPosts,
    PostAnalysisResult,
    QueueMessage,
)

from query_processor.config import config

from prometheus_client import Histogram, Counter

result_queue_wait_time = Histogram(
    'result_queue_wait_time_seconds',
    'Result queue wait time',
)
query_results = Counter('query_results_total', 'Query results', ['status'])

async def queue_scrape_request(query, query_processor_id, app):
    """Create and queue a scrape request with specified parameters."""
    body = AnalysisRequest(query_processor_id=query_processor_id,
                           code=ANALYSIS_REQUEST,
                           parameters=query)
    message = Message(body=body.model_dump_json(by_alias=True).encode('utf-8'))
    await send_message(app.state.channel.default_exchange, message,
                       config.RABBIT_MQ.ANALYSIS_REQUEST_QUEUE, app.state.logger)

async def receive_analysis_results(query_processor_id, app):
    """Create queue and await each message."""
    queue = await declare_queue(app.state.channel,
                                config.RABBIT_MQ.ANALYSIS_RESULT_QUEUE,
                                app.state.logger)
    try:
        await queue.bind(app.state.results_exchange, routing_key=query_processor_id)
    except ChannelClosed:
        app.state.logger.error("Channel closed while declaring/binding results queue.")
        raise
    except (AMQPConnectionError, ConnectionClosed):
        app.state.logger.error("Connection lost while declaring/binding results queue.")
        raise
    except Exception as e:
        app.state.logger.error("Unexpected error while declaring/binding results queue: %s", e)
        raise
    analysis_results = []
    hashed_results = set()
    try:
        async def process_messages():
            messages_left = None
            async with queue.iterator() as iterator:
                async for message in iterator:
                    async with message.process():
                        messages_left = done_receiving_messages(message,
                                                                analysis_results,
                                                                hashed_results,
                                                                messages_left,
                                                                app)
                        if messages_left == 0:
                            break
            return analysis_results
        with result_queue_wait_time.time():
            result = await asyncio.wait_for(process_messages(), timeout=config.TIMEOUT)
        query_results.labels(status='success').inc()
        return result

    except TimeoutError:
        query_results.labels(status='timeout').inc()
        app.state.logger.warning("Request timeout")
        return analysis_results

    finally:
        try:
            await queue.unbind(app.state.results_exchange, routing_key=query_processor_id)
            await queue.delete(if_unused=False, if_empty=False)
        except Exception as e:
            app.state.logger.warning("Unexpected error on queue unbind/delete: %s", e)

def done_receiving_messages(message: Message,
                            analysis_results: list[PostAnalysisResult],
                            hashed_results: set[str],
                            messages_left: int | None,
                            app):
    """Return amount of messages expected or None if it's still unknown."""
    decoded_body = message.body.decode("utf-8")
    queue_message = QueueMessage.model_validate_json(decoded_body)
    if queue_message.code == POST_ANALYSIS_RESULT:
        post = PostAnalysisResult.model_validate_json(decoded_body)
        post = post.model_dump()
        post.pop("query_processor_id", None)
        post.pop("code", None)
        analysis_results.append(post)
        if messages_left is not None:
            return messages_left - 1
        return None
    elif queue_message.code == EOF:
        post = EndOfPosts.model_validate_json(decoded_body)
        return post.total - len(analysis_results)
    else:
        app.state.logger.warning("Unknown message code %d", queue_message.code)
    return messages_left
