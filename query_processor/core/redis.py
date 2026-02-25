import json

from redis.asyncio import Redis
from util.schemas import SearchParameters

redis = Redis(
    host="redis",
    port=6379,
    decode_responses=True,  # store strings, not bytes
)

def make_cache_key(params : SearchParameters) -> str:
    """Construct cache key for Redis based on query parameters."""
    payload = params.model_dump(
        mode="json",
        by_alias=True,
        exclude={"emotions"},
    )
    payload["keywords"] = sorted(k.lower() for k in payload["keywords"])
    payload["platform"] = sorted(payload["platform"])
    key = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )
    return key
