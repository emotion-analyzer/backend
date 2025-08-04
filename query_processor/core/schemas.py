from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AnalysisParams(BaseModel):
    date_start: datetime
    date_end: Optional[datetime] = datetime.now()
    keyword: str
    platform: list[str] = ["all"]
    limit: int = 100


class PostRequest(BaseModel):
    query_processor_id: str
    analysis_parameters: AnalysisParams

class QueueMessage(BaseModel):
    code: int
    query_processor_id: str
    model_config = ConfigDict(extra='allow')

class Post(QueueMessage):
    """Post object."""
    link: str
    text: str
    timestamp: datetime

class PostAnalysisResult(Post):
    """Inference batch response."""
    affective_states: dict[str, float]
    dominant_affective_state: str