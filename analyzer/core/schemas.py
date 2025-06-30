from datetime import datetime

from pydantic import BaseModel


class AnalyzePrompt(BaseModel):
    """Single inference request."""

    text: str


class AnalyzePromptResponse(BaseModel):
    """Inference response."""

    emotions: dict[str, float]
    dominant_emotion: str

class Post(BaseModel):
    """Post object."""
    link: str
    text: str
    timestamp: datetime


class AnalyzePromptBatch(BaseModel):
    """Inference batch request."""

    posts: list[Post]


class BatchResponse(BaseModel):
    """Inference batch response."""

    link: str
    text: str
    dominant_emotion: str


class AnalyzeBatchResponse(BaseModel):
    """Single inference response."""
    predictions: list[BatchResponse]

