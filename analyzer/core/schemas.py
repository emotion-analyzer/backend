
from pydantic import BaseModel


class AnalyzePrompt(BaseModel):
    """Single inference request."""

    text: str


class AnalyzePromptResponse(BaseModel):
    """Single inference response."""

    emotions: dict[str, float]
    mapped_emotions: dict[str, float]
    dominant_emotion: str


class AnalyzePromptBatch(BaseModel):
    """Inference batch request."""

    texts: list[str]


class BatchResponse(BaseModel):
    """Inference batch response."""

    text: str
    dominant_emotion: str


class AnalyzeBatchResponse(BaseModel):
    """Single inference response."""
    predictions: list[BatchResponse]

