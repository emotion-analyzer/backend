from datetime import datetime

from pydantic import BaseModel


class FetchQuery(BaseModel):
    """Model for fetching social media posts ."""
    date_start: datetime
    date_end: datetime | None = datetime.now()
    keyword: str
    platform: list[str] = ["all"]
    limit: int = 100

class Post(BaseModel):
    """Post object."""
    link: str
    text: str
    timestamp: datetime

class FetchResult(BaseModel):
    """Result of a social media post-fetch."""
    results: list[Post]
