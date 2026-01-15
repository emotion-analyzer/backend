from datetime import datetime

from util.schemas import PostAnalysisResult

from elasticsearch import NotFoundError


def store_query(text_hash: str, model_version: str,
                analyzed_post:PostAnalysisResult, client) -> None:
    """Store query for faster lookup."""
    document = analyzed_post.model_dump()
    document.pop("query_processor_id", None)
    document["processing_timestamp"] = datetime.now().isoformat()
    document["version"] = model_version
    client.index(index="analysis-current", id=text_hash,
                 document=document)

def look_up_query(text_hash: str, client):
    """Get query result for given text hash or None if not found."""
    try:
        result = client.get(index="analysis-current", id=text_hash)
    except NotFoundError:
        return None
    source = result.get("_source")
    source.pop("processing_timestamp", None)
    return source
