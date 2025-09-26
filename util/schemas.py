from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class QueueMessage(BaseModel):
    """General queue message model."""
    query_processor_id: str
    code: int

class AnalysisRequestParameters(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime] = datetime.now()
    language: Optional[str] = "es"
    keywords: list[str]
    platform: list[str] = ["all"]
    model: str

class SearchParameters(AnalysisRequestParameters):
    emotions: list[str] = ["all"]

class AnalysisRequest(QueueMessage):
    parameters: AnalysisRequestParameters

class Post(QueueMessage):
    """Social media post model."""
    source: str
    link: str
    text: str
    timestamp: datetime
    model: str


class PostAnalysisResult(Post):
    """Social media analysis result model."""
    model: str
    affective_states: dict[str, float]
    dominant_emotion: str | None = None


class EndOfPosts(QueueMessage):
    """Model for message sent when finished scraping."""
    total: int