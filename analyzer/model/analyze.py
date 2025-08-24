from util.schemas import Post, PostAnalysisResult

from analyzer.core.hashing import compute_text_hash
from analyzer.result_storage.crud import look_up_query, store_query


def analyze_post(available_models, db, post: Post):
    """Return stored affective state analysis or process and store the result."""
    # This should be acquired from the post
    model_placeholder = "masked_language"
    text_hash = compute_text_hash(post.text + model_placeholder)
    prompt_analysis = look_up_query(text_hash, db)
    if prompt_analysis is None:
        model = available_models[model_placeholder]
        affective_states = model.process(post)
        prompt_analysis = PostAnalysisResult(**post.model_dump(),
                                             model=model_placeholder,
                                             affective_states=affective_states)
        store_query(text_hash,prompt_analysis, db)
    else:
        prompt_analysis = PostAnalysisResult(**prompt_analysis)
    return prompt_analysis
