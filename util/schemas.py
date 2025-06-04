from datetime import datetime

from pydantic import BaseModel


class FetchRequest(BaseModel):
    """Request for social media post-fetching."""
    platform: str
    query: str
    limit: int

class Post(BaseModel):
    """Post object."""
    id: str
    text: str
    timestamp: datetime

class FetchResult(BaseModel):
    """Result of a social media post-fetch."""
    results: list[Post]
