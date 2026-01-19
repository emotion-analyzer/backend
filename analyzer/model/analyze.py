from util.codes import POST_ANALYSIS_RESULT
from util.schemas import Post, PostAnalysisResult

from analyzer.core.hashing import compute_text_hash
from analyzer.core.metrics import elasticsearch_operation_duration, requests, score
from elasticsearch.helpers import bulk


def analyze_post(available_models, post: Post, logger):
    """Return stored affective state analysis or process and store the result."""
    model_name = f"{post.language}_{post.model}"
    model = available_models.get(model_name, None)
    if model is None:
        logger.warning(f"No model found for {model_name}.")
        return None
    affective_states = model.process(post.text)
    if len(affective_states) > 0:
        largest_key = max(affective_states, key=affective_states.get)
        largest_value = affective_states[largest_key]
        score.labels(model=post.model).inc(largest_value)
    requests.labels(model=post.model).inc()
    prompt_analysis = PostAnalysisResult(**post.model_dump(),
                                         affective_states=affective_states)
    return prompt_analysis

def get_hash(post: Post):
    """Return post hash for ES indexing."""
    model_name = f"{post.language}_{post.model}"
    text_hash = compute_text_hash(post.text + model_name)
    return text_hash

def bulk_analyze_posts(available_models, client, documents: list[Post], logger):
    """Retrieve/analyze posts and then store them if needed."""
    docs_dict = {get_hash(doc):doc for doc in documents}
    if len(documents) == 0:
        return []

    with elasticsearch_operation_duration.labels(operation='es_lookup').time():
        resp = client.mget(
            index="analysis-current",
            body={"ids": list(docs_dict.keys())},
            _source=True
        )

    existing_results = []
    missing_results = []

    # Obtengo las respuestas o las genero segun sea necesario
    for item in resp["docs"]:
        doc_id = item["_id"]
        if item["found"]:
            prompt_analysis = dict(item["_source"])
            prompt_analysis["query_processor_id"] = docs_dict[doc_id].query_processor_id
            prompt_analysis = PostAnalysisResult(**prompt_analysis)
            prompt_analysis.code = POST_ANALYSIS_RESULT
            existing_results.append(prompt_analysis)
        else:
            prompt_analysis = analyze_post(available_models, docs_dict[doc_id], logger)
            prompt_analysis.code = POST_ANALYSIS_RESULT
            missing_results.append(prompt_analysis)

    # Realizo un intento de guardar las respuestas
    actions = [
        {
            "_op_type": "index",
            "_index": "analysis-current",
            "_id": get_hash(doc),
            "_source": doc.model_dump()
        }
        for doc in missing_results
    ]

    with elasticsearch_operation_duration.labels(operation='es_insert').time():
        bulk(
            client,
            actions,
            chunk_size=1000,
            max_chunk_bytes=10 * 1024 * 1024,
            raise_on_error=False,
            max_retries=3,
            initial_backoff=2
        )

    return existing_results + missing_results
