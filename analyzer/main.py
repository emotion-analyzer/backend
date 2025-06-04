from contextlib import asynccontextmanager

from fastapi import Request, FastAPI

from analyzer.config import config
from analyzer.core.schemas import AnalyzePrompt, AnalyzePromptBatch, BatchResponse
from analyzer.model.initialization import load_emotions_model
from analyzer.model.prediction import make_new_prediction
from util.database_session import SessionDep, create_db_and_tables, init_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the model and tokenizer before the app runs."""
    init_engine(config.DATABASE.URL_)
    create_db_and_tables()
    app.state.tokenizer, app.state.pipeline = load_emotions_model()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/text")
async def analyze_text(prompt: AnalyzePrompt,
                       request: Request,
                       session: SessionDep):
    """ Perform emotion analysis on the received text.

    Returns:
        result: the resulting id for the new registered user.
    """
    prediction = make_new_prediction(request.app.state.tokenizer,
                                     request.app.state.pipeline,
                                     prompt.text,
                                     session)
    return {"result": prediction}


@app.post("/batch")
async def analyze_text(request: Request,
                       prompt: AnalyzePromptBatch,
                       session: SessionDep):
    """ Perform emotion analysis on the received text batch.

    Returns:
        id: the resulting id for the new registered user.
    """
    predictions = []
    for text in prompt.texts:
        predictions.append(BatchResponse
            (text=text,
             dominant_emotion=make_new_prediction(request.app.state.tokenizer,
                                                  request.app.state.pipeline,
                                                  text,
                                                  session).dominant_emotion))
    return {"results": predictions}
