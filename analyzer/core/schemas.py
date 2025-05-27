from typing import List

from pydantic import BaseModel

class AnalyzePrompt(BaseModel):
    """Single inference request."""

    text: str


class AnalyzePromptResponse(BaseModel):
    """Single inference response."""

    emotions: dict[str, float]
    dominant_emotion: str


class AnalyzePromptBatch(BaseModel):
    """Inference batch request."""

    texts: List[str]


class BatchResponse(BaseModel):
    """Inference batch response."""
    text: str
    dominant_emotion: str


class AnalyzeBatchResponse(BaseModel):
    """Single inference response."""
    predictions: List[BatchResponse]

