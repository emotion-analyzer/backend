from datetime import datetime

from pydantic import BaseModel


class FetchQuery(BaseModel):
    """Details for fetching social media posts."""
    date_start: datetime
    date_end: datetime | None = datetime.now()
    keyword: str
    platform: list[str] = ["all"]
    limit: int = 100

class PostRequest(BaseModel):
    """Model for fetching social media posts."""
    query_processor_id: str
    analysis_parameters: FetchQuery

class QueueMessage(BaseModel):
    """General queue message model."""
    query_processor_id: str
    code: int

class Post(QueueMessage):
    """Social media post model."""
    link: str
    text: str
    timestamp: datetime
