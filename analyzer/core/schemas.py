from typing import List

from pydantic import BaseModel, EmailStr


class AnalyzePrompt(BaseModel):
    """Single inference request."""

    text: str

class AnalyzePromptResponse(BaseModel):
    """Single inference response."""

    emotions: List[str]
    dominant_emotion: str

class AnalyzePromptBatch(BaseModel):
    """Inference batch request."""

    texts: List[str]