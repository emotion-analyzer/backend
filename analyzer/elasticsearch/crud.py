from elasticsearch import NotFoundError
from util.schemas import PostAnalysisResult


def store_query(text_hash: str, analyzed_post:PostAnalysisResult, client) -> None:
    """Store query for faster lookup."""
    client.index(index="analysis_index", id=text_hash,
                 document=analyzed_post.model_dump())

def look_up_query(text_hash: str, client):
    """Get query result for given text hash or None if not found."""
    try:
        result = client.get(index="analysis_index", id=text_hash)
    except NotFoundError:
        return None
    return result.get("_source")
