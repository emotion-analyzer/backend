from util.codes import POST_ANALYSIS_RESULT
from util.schemas import Post, PostAnalysisResult

from analyzer.core.hashing import compute_text_hash
from analyzer.core.metrics import requests, score
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk


def analyze_post_batch(available_models, posts: list[Post], logger):
    """Groups posts by model and runs batch inference for each group."""
    groups = {}
    for p in posts:
        m_name = f"{p.language}_{p.model}"
        groups.setdefault(m_name, []).append(p)
    all_results = []
    for m_name, group_posts in groups.items():
        model = available_models.get(m_name)
        if not model:
            logger.warning(f"No model: {m_name}")
            continue
        batch_states = model.process_batch([p.text for p in group_posts])
        for post, states in zip(group_posts, batch_states):
            if states:
                largest = max(states, key=states.get)
                score.labels(model=post.model).inc(states[largest])
            requests.labels(model=post.model).inc()
            result = PostAnalysisResult(
                **post.model_dump(),
                affective_states=states,
                id=get_hash(post))
            result.code = POST_ANALYSIS_RESULT
            all_results.append(result)
    return all_results

def get_hash(post: Post):
    """Return post hash for ES indexing."""
    model_name = f"{post.language}_{post.model}"
    text_hash = compute_text_hash(post.text + model_name)
    return text_hash

async def bulk_analyze_posts(available_models, client: AsyncElasticsearch,
                             documents: list[Post], logger):
    docs_dict = {get_hash(doc): doc for doc in documents}
    if not documents:
        return []

    resp = await client.mget(
        index="analysis-current",
        body={"ids": list(docs_dict.keys())},
        _source=True
    )

    existing_results = []

    docs_for_processing = []
    for item in resp["docs"]:
        doc_id = item["_id"]
        if item["found"] and item.get("_source") is not None:
            res_data = item["_source"]
            res_data["query_processor_id"] = docs_dict[doc_id].query_processor_id
            res_data["code"] = POST_ANALYSIS_RESULT
            res_data["id"] = doc_id
            existing_results.append(PostAnalysisResult(**res_data))
        else:
            docs_for_processing.append(docs_dict[doc_id])
    missing_results = analyze_post_batch(available_models, docs_for_processing, logger)

    actions = [
        {
            "_op_type": "index",
            "_index": "analysis-current",
            "_id": get_hash(doc),
            "_source": doc.model_dump()
        }
        for doc in missing_results
    ]

    if actions:
        await async_bulk(client, actions)

    return existing_results + missing_results
