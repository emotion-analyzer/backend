from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI
from util.models import available_models
from util.schemas import (
    AnalysisRequestParameters,
    SearchParameters,
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

@app.post("/search")
async def get_emotional_analysis (query_parameters : SearchParameters):
    """Request social media posts and their corresponding emotional analysis."""
    query_processor_id = str(uuid.uuid4())
    await queue_scrape_request(query_parameters, query_processor_id, app)
    analysis_results = await receive_analysis_results(query_processor_id, app)
    analysis_results = map_to_fixed_labels(analysis_results, query_parameters.emotions)
    return {"results": analysis_results}


@app.get("/models")
async def get_available_models (query_parameters : AnalysisRequestParameters):
    """Return all available models for emotional analysis."""
    return {"models": available_models}
