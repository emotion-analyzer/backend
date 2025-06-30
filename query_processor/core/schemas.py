from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class EmotionalAnalysisParams(BaseModel):
    date_start: datetime
    date_end: Optional[datetime] = datetime.now()
    keyword: str
    platform: list[str] = ["all"]
    limit: int = 100