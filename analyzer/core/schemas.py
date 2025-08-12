from datetime import datetime

from pydantic import BaseModel, ConfigDict


class QueueMessage(BaseModel):
    """General queue message model."""
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
