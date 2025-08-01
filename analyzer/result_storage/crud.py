from elasticsearch import NotFoundError

from analyzer.core.schemas import AnalyzePromptResponse


def store_query(text_hash: str, analysis_result: AnalyzePromptResponse, client) -> None:
    """Store query for faster lookup."""
    client.index(index="analysis_index", id=text_hash, document=analysis_result.dict())


def look_up_query(text_hash: str, client):
    """Get query result for given text hash or None if not found."""
    try:
        result = client.get(index="analysis_index", id=text_hash)
    except NotFoundError:
        return None
    return result.get("_source")
