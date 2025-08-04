# ruff: noqa: RUF006
import uuid

from contextlib import asynccontextmanager
from typing import Annotated

from aio_pika import Message
from fastapi import FastAPI, Query

from query_processor.core.codes import POST
from query_processor.core.queue_middleware import initiate_connection, initialize_queues
from query_processor.core.schemas import AnalysisParams, PostRequest, QueueMessage, Post
from query_processor.config import config
from query_processor.stats.aggregation import process_affective_states


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the rabbitQ connection."""
    app.state.channel = await initiate_connection(config)
    app.state.posts_queue, app.state.results_exchange = await initialize_queues(app.state.channel, config)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def get_emotional_analysis (query: Annotated[AnalysisParams, Query()]):
    """Request social media posts and their corresponding emotional analysis."""
    query_processor_id = str(uuid.uuid4())
    body = PostRequest(query_processor_id=query_processor_id,
                       analysis_parameters=query)
    message = Message(body=body.model_dump_json().encode('utf-8'))
    await app.state.channel.default_exchange.publish(
        message,
        routing_key=app.state.posts_queue.name,
    )
    queue = await app.state.channel.declare_queue("results", durable=True)
    await queue.bind(app.state.results_exchange, routing_key=query_processor_id)
    analysis_results= []
    affective_states = []
    async with queue.iterator() as iterator:
        async for message in iterator:
            async with message.process():
                queue_message = QueueMessage.model_validate_json(message.body.decode("utf-8"))
                if queue_message.code == POST:
                    post = Post.model_validate_json(message.body.decode("utf-8"))
                    affective_states.extend(list(post.affective_states.keys()))
                    post = post.model_dump()
                    post.pop("query_processor_id", None)
                    post.pop("code", None)
                    analysis_results.append(post)
                else:
                    break
    await queue.delete()
    as_summary, mapped_summary = process_affective_states(affective_states)
    return {"posts": analysis_results,
            "affective_states": as_summary,
            "mapped_summary": mapped_summary}