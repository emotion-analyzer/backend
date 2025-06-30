import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from analyzer.config import config
from analyzer.core.queue_middleware import process_posts
from analyzer.core.schemas import AnalyzePrompt, AnalyzePromptBatch, BatchResponse
from analyzer.database.session import SessionDep, create_db_and_tables, engine
from analyzer.model.initialization import load_emotions_model
from analyzer.model.analyze import analyze_text
from analyzer.stats.aggregation import process_affective_states


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the model and tokenizer before the app runs."""
    create_db_and_tables()
    app.state.tokenizer, app.state.model = load_emotions_model()
    app.state.process_task = asyncio.create_task(process_posts(app.state.tokenizer,
                                                               app.state.model,
                                                               engine,
                                                               config))
    yield
    app.state.process_task.cancel()

app = FastAPI(lifespan=lifespan)

@app.post("/batch")
async def analyze_text_batch(prompt: AnalyzePromptBatch,
                             request: Request,
                             session: SessionDep):
    """Perform emotion analysis on the received text batch.

    Returns:
        id: the resulting id for the new registered user.
    """
    analysis_results = []
    affective_states = []
    for post in prompt.posts:
        affective_state = analyze_text(request.app.state.tokenizer,
                                      request.app.state.model,
                                      post.text,
                                      session).dominant_emotion
        analysis_results.append(BatchResponse(link=post.link,
                                              text=post.text,
                                              dominant_emotion=affective_state))
        affective_states.append(affective_state)
    as_summary, mapped_summary = process_affective_states(affective_states)
    return {"posts": analysis_results,
            "affective_states": as_summary,
            "mapped_summary": mapped_summary}
