from contextlib import asynccontextmanager
import json
import logging
import uuid

from fastapi import Depends, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.status import HTTP_401_UNAUTHORIZED
from util.logging import initialize_logging
from util.queue_middleware import (
    configure,
    declare_queue,
    initialize_exchange,
    initiate_connection,
)
from util.schemas import SearchParameters

from query_processor.config import config
from query_processor.core.redis import make_cache_key, redis
from query_processor.core.security import decode_token
from query_processor.core.util import queue_scrape_request, receive_analysis_results
from query_processor.exceptions.exceptions import AuthError
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
    await configure(app.state.channel, config.RABBIT_MQ.PREFETCH_COUNT)
    await declare_queue(app.state.channel,
                        config.RABBIT_MQ.ANALYSIS_REQUEST_QUEUE,
                        app.state.logger)
    app.state.results_exchange = await initialize_exchange(app.state.channel,
                                                           config.RABBIT_MQ.RESULT_EXCHANGE,
                                                           app.state.logger)
    instrumentator.expose(app)
    app.state.logger.info("Service initialized")
    yield

app = FastAPI(lifespan=lifespan)
instrumentator = Instrumentator().instrument(app)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Metrics
analysis_requests = Counter('analysis_requests_total', 'Analysis requests')

@app.post("/search")
async def get_emotional_analysis (query_parameters : SearchParameters,
                                  access_token: str = Depends(oauth2_scheme)
                                  ):
    """Request social media posts and their corresponding emotional analysis."""
    analysis_requests.inc()
    all_emotions = ["surprise", "joy", "fear", "anger", "sadness", "disgust"]
    if set(all_emotions) <= set(query_parameters.emotions):
        query_parameters.emotions = ["all"]
    cache_key = make_cache_key(query_parameters)
    cached_results = await redis.get(cache_key)
    if cached_results:
        if "all" in query_parameters.emotions:
            results = json.loads(cached_results)
        else:
            full_results = json.loads(cached_results)
            results = [result for result in full_results if
                       result["dominant_emotion"]["label"] in query_parameters.emotions]
        return {"results": results}
    try:
        decode_token(access_token)
    except AuthError as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=e.message) from e
    query_processor_id = str(uuid.uuid4())
    await queue_scrape_request(query_parameters, query_processor_id, app)
    analysis_results = await receive_analysis_results(query_processor_id, app)
    analysis_results = map_to_fixed_labels(analysis_results)
    # We only cache the results if theres at least 1
    if len(analysis_results) > 0:
        analysis_results_json = jsonable_encoder(analysis_results)
        await redis.set(cache_key, json.dumps(analysis_results_json))
    if "all" in query_parameters.emotions:
        results = analysis_results
    else:
        results = [result for result in analysis_results if
            result["dominant_emotion"].label in query_parameters.emotions]
    return {"results": results}
