# ruff: noqa: RUF006
import uuid

from contextlib import asynccontextmanager
from typing import Annotated

from aio_pika import Message
from fastapi import FastAPI, Query

from query_processor.fasttext.fasttext_mapping import map_to_ekman_fasttext
from util.codes import ANALYSIS_REQUEST, POST_ANALYSIS_RESULT, EOF
from query_processor.core.queue_middleware import initiate_connection, initialize_queues
from util.schemas import AnalysisRequestParameters, QueueMessage, PostAnalysisResult, AnalysisRequest, EndOfPosts
from query_processor.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the rabbitQ connection."""
    app.state.channel = await initiate_connection(config)
    app.state.posts_queue, app.state.results_exchange = await initialize_queues(app.state.channel, config)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def get_emotional_analysis (query: Annotated[AnalysisRequestParameters, Query()]):
    """Request social media posts and their corresponding emotional analysis."""
    query_processor_id = str(uuid.uuid4())
    body = AnalysisRequest(query_processor_id=query_processor_id,
                       code=ANALYSIS_REQUEST,
                       parameters=query)
    message = Message(body=body.model_dump_json().encode('utf-8'))
    await app.state.channel.default_exchange.publish(
        message,
        routing_key=app.state.posts_queue.name,
    )
    queue = await app.state.channel.declare_queue(config.RABBIT_MQ.ANALYSIS_RESULT_QUEUE, durable=True)
    await queue.bind(app.state.results_exchange, routing_key=query_processor_id)
    analysis_results= []
    posts_awaited = None
    async with queue.iterator() as iterator:
        async for message in iterator:
            async with message.process():
                queue_message = QueueMessage.model_validate_json(message.body.decode("utf-8"))
                if queue_message.code == POST_ANALYSIS_RESULT:
                    post = PostAnalysisResult.model_validate_json(message.body.decode("utf-8"))
                    post = post.model_dump()
                    post.pop("query_processor_id", None)
                    post.pop("code", None)
                    analysis_results.append(post)
                    if posts_awaited is not None:
                        if len(analysis_results) == posts_awaited:
                            break
                elif queue_message.code == EOF:
                    post = EndOfPosts.model_validate_json(message.body.decode("utf-8"))
                    posts_awaited = post.total
                    if len(analysis_results) == posts_awaited:
                        break
    map_to_ekman_fasttext(analysis_results)
    return {"results": analysis_results}