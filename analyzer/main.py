import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from analyzer.config import config
from analyzer.core.queue_middleware import process_posts
from analyzer.core.schemas import AnalyzePromptBatch, BatchResponse
from analyzer.model.analyze import get_affective_states
from analyzer.model.initialization import load_emotions_model
from analyzer.result_storage.initialization import initialize_mappings
from analyzer.stats.aggregation import process_affective_states


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the model and tokenizer before the app runs."""
    app.state.elasticsearch_client = initialize_mappings()
    app.state.tokenizer, app.state.model = load_emotions_model()
    app.state.process_task = asyncio.create_task(process_posts(app.state.tokenizer,
                                                               app.state.model,
                                                               app.state.elasticsearch_client,
                                                               config))
    yield
    app.state.process_task.cancel()

app = FastAPI(lifespan=lifespan)

@app.post("/batch")
async def get_affective_states_batch(prompt: AnalyzePromptBatch,
                                     request: Request):
    """Perform emotion analysis on the received text batch.

    Returns:
        posts: the resulting id for the new registered user.
    """
    analysis_results = []
    affective_states = []
    for post in prompt.posts:
        analysis_result = get_affective_states(
            request.app.state.tokenizer,
            request.app.state.model,
            request.app.state.elasticsearch_client,
            post.text)
        analysis_results.append(BatchResponse(link=post.link,
                                              text=post.text,
                                              affective_states=list(analysis_result.affective_states.keys()),
                                              dominant_affective_state=analysis_result.dominant_affective_state))
        affective_states.extend(list(analysis_result.affective_states.keys()))
    as_summary, mapped_summary = process_affective_states(affective_states)
    return {"posts": analysis_results,
            "affective_states": as_summary,
            "mapped_summary": mapped_summary}
