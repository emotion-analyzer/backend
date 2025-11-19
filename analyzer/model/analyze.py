from util.schemas import Post, PostAnalysisResult

from analyzer.core.hashing import compute_text_hash
from analyzer.elasticsearch.crud import look_up_query, store_query


def analyze_post(available_models, db, post: Post, logger):
    """Return stored affective state analysis or process and store the result."""
    model_name = f"{post.language}_{post.model}"
    text_hash = compute_text_hash(post.text + model_name)
    prompt_analysis = look_up_query(text_hash, db)
    if prompt_analysis is None:
        model = available_models.get(model_name, None)
        if model is None:
            logger.warning(f"No model found for {model_name}.")
            return None
        affective_states = model.process(post.text)
        prompt_analysis = PostAnalysisResult(**post.model_dump(),
                                             affective_states=affective_states)
        store_query(text_hash, prompt_analysis, db)
    else:
        prompt_analysis = PostAnalysisResult(**prompt_analysis)
    return prompt_analysis
