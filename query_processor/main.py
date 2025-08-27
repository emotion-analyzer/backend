from contextlib import asynccontextmanager
from typing import Annotated
import uuid

from fastapi import FastAPI, Query
from util.schemas import (
    AnalysisRequestParameters,
)

from query_processor.config import config
from query_processor.core.queue_middleware import (
    initialize_exchange,
    initialize_queues,
    initiate_connection,
)
from query_processor.core.util import queue_scrape_request, receive_analysis_results
from query_processor.fasttext.mapping import map_to_fixed_labels


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the rabbitQ connection."""
    app.state.channel = await initiate_connection(config)
    app.state.posts_queue = await initialize_queues(app.state.channel, config)
    app.state.results_exchange = await initialize_exchange(app.state.channel, config)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def get_emotional_analysis (query: Annotated[AnalysisRequestParameters, Query()]):
    """Request social media posts and their corresponding emotional analysis."""
    query_processor_id = str(uuid.uuid4())
    await queue_scrape_request(query, query_processor_id, app)
    # There should be a fixed timeout
    analysis_results = await receive_analysis_results(query_processor_id, app)
    map_to_fixed_labels(analysis_results)
    return {"results": analysis_results}
