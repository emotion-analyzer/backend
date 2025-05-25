from contextlib import asynccontextmanager

from fastapi import Request, FastAPI

from analyzer.core.schemas import AnalyzePrompt, AnalyzePromptResponse
from analyzer.model.initialization import load_emotions_model
from analyzer.model.prediction import make_new_prediction


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the model and tokenizer before the app runs."""
    app.state.tokenizer, app.state.model = load_emotions_model()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/text")
async def analyze_text(request: Request,
                       prompt: AnalyzePrompt):
    """ Make a prediction for the received text.

    Returns:
        id: the resulting id for the new registered user.
    """
    prediction = make_new_prediction(request.app.state.tokenizer,
                                     request.app.state.model,
                                     prompt)
    return {"prediction": prediction}

