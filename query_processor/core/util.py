from aio_pika import Message
from util.codes import ANALYSIS_REQUEST, EOF, POST_ANALYSIS_RESULT
from util.schemas import (
    AnalysisRequest,
    EndOfPosts,
    PostAnalysisResult,
    QueueMessage,
)

from query_processor.config import config


async def queue_scrape_request(query, query_processor_id, app):
    """Create and queue a scrape request with specified parameters."""
    body = AnalysisRequest(query_processor_id=query_processor_id,
                           code=ANALYSIS_REQUEST,
                           parameters=query)
    message = Message(body=body.model_dump_json(by_alias=True).encode('utf-8'))
    await app.state.channel.default_exchange.publish(
        message,
        routing_key=app.state.posts_queue.name,
    )

async def receive_analysis_results(query_processor_id, app):
    """Create queue and await each message."""
    queue = await app.state.channel.declare_queue(config.RABBIT_MQ.ANALYSIS_RESULT_QUEUE,
                                                  durable=True)
    await queue.bind(app.state.results_exchange, routing_key=query_processor_id)
    analysis_results = []
    messages_left = None
    async with queue.iterator() as iterator:
        async for message in iterator:
            async with message.process():
                messages_left = done_receiving_messages(message,
                                                        analysis_results,
                                                        messages_left)
                if messages_left == 0:
                    break
    return analysis_results

def done_receiving_messages(message: Message,
                            analysis_results: list[PostAnalysisResult],
                            messages_left: int | None):
    """Return amount of messages expected or None if its unknown."""
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
    return messages_left
