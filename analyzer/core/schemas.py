from datetime import datetime

from pydantic import BaseModel


class AnalyzePromptResponse(BaseModel):
    """Inference response."""

    affective_states: dict[str, float]
    dominant_affective_state: str


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
    affective_states: list[str]
    dominant_affective_state: str

