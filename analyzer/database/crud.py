
from sqlmodel import select
from util.database_session import SessionDep

from analyzer.core.schemas import AnalyzePromptResponse
from analyzer.database.model import QueryResult


def store_query(text_hash: str, result: AnalyzePromptResponse,
                session: SessionDep) -> None:
    """Store query for faster lookup."""
    query_result = QueryResult(
        text_hash=text_hash,
        emotions=result.emotions,
        dominant_emotion=result.dominant_emotion)
    session.add(query_result)
    session.commit()
    session.refresh(query_result)


def look_up_query(text_hash: str,
                  session: SessionDep) -> QueryResult | None:
    """Get query result for given text hash or None if not found."""
    statement = select(QueryResult).where(QueryResult.text_hash == text_hash)
    return session.exec(statement).first()
