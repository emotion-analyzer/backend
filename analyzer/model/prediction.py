from analyzer.core.hashing import compute_text_hash
from analyzer.core.schemas import AnalyzePromptResponse
from analyzer.database.crud import look_up_query, store_query
from analyzer.database.session import SessionDep


def get_emotional_analysis(tokenizer, pipeline,
                           prompt: str, top_k:int = 5):
    """Perform an emotional analysis and store it in the database."""
    results = pipeline(f"{prompt} Me siento {tokenizer.mask_token}.", top_k=top_k)
    emotions_with_scores = {}
    for result in results:
        emotions_with_scores[result['token_str']] = float(result['score'])
    return AnalyzePromptResponse(emotions=emotions_with_scores,
                                 dominant_emotion=results[0]['token_str'])


def make_new_prediction(tokenizer, pipeline, prompt: str,
                        session: SessionDep, top_k:int = 5):
    """Return stored analysis or process the text and store the result."""
    text_hash = compute_text_hash(prompt)
    prompt_analysis = look_up_query(text_hash, session)
    if prompt_analysis is not None:
        return AnalyzePromptResponse(emotions=prompt_analysis.emotions,
                                     dominant_emotion=prompt_analysis.dominant_emotion)
    else:
        result = get_emotional_analysis(tokenizer, pipeline, prompt, top_k)
        store_query(text_hash, result, session)
        return result
