
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON
from sqlmodel import Field, SQLModel


class QueryResult(SQLModel, table=True):
    """Represents the result of a query after emotional analysis."""

    text_hash: str = Field(index=True, default=None, primary_key=True, max_length=64)
    emotions: dict[str, float] = Field(default=None, sa_column=Column(JSON))
    mapped_emotions: dict[str, float] = Field(default=None, sa_column=Column(JSON))
    dominant_emotion: str = Field(default=None,nullable=True)

