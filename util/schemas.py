from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class QueueMessage(BaseModel):
    """General queue message model."""
    query_processor_id: str
    code: int


class AnalysisRequestParameters(BaseModel):
    date_start: datetime
    date_end: Optional[datetime] = datetime.now()
    keyword: str
    platform: list[str] = ["all"]
    limit: int = 100


class AnalysisRequest(QueueMessage):
    parameters: AnalysisRequestParameters


class Post(QueueMessage):
    """Social media post model."""
    source: str
    link: str
    text: str
    timestamp: datetime


class PostAnalysisResult(Post):
    """Social media analysis result model."""
    model: str
    affective_states: dict[str, float]
    dominant_emotions: list[str] | None = None


class EndOfPosts(QueueMessage):
    """Model for message sent when finished scraping."""
    total: int