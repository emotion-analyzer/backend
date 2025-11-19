import logging
from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI

from util.queue_middleware import initiate_connection, declare_queue, initialize_exchange
from util.logging import initialize_logging
from util.schemas import SearchParameters

from query_processor.config import config
from query_processor.core.util import queue_scrape_request, receive_analysis_results
from query_processor.fasttext.mapping import map_to_fixed_labels

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize logging and rabbitMQ connection."""
    initialize_logging(config.FLUENTD.HOST,
                       config.FLUENTD.PORT,
                       "query_processor")
    app.state.logger = logging.getLogger("affect_pulse")
    app.state.connection = await initiate_connection(config)
    app.state.channel = await app.state.connection.channel()
    # Mover esto a middleware
    await app.state.channel.set_qos(prefetch_count=config.RABBIT_MQ.PREFETCH_COUNT)
    await declare_queue(app.state.channel,
                        config.RABBIT_MQ.ANALYSIS_REQUEST_QUEUE,
                        app.state.logger)
    app.state.results_exchange = await initialize_exchange(app.state.channel,
                                                           config.RABBIT_MQ.RESULT_EXCHANGE,
                                                           app.state.logger)
    app.state.logger.info("Service initialized")
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
