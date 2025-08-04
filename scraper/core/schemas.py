from datetime import datetime

from pydantic import BaseModel


class FetchQuery(BaseModel):
    """Model for fetching social media posts ."""
    date_start: datetime
    date_end: datetime | None = datetime.now()
    keyword: str
    platform: list[str] = ["all"]
    limit: int = 100

class PostRequest(BaseModel):
    query_processor_id: str
    analysis_parameters: FetchQuery

class QueueMessage(BaseModel):
    query_processor_id: str
    code: int

class Post(QueueMessage):
    """Post object."""
    link: str
    text: str
    timestamp: datetime