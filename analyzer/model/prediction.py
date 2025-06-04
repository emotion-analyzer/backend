from analyzer.core.hashing import compute_text_hash
from analyzer.core.schemas import AnalyzePromptResponse
from analyzer.database.crud import look_up_query, store_query
from util.database_session import SessionDep


def get_emotional_analysis(tokenizer, pipeline, prompt: str, TOP_K:int = 5):
    results = pipeline(f"{prompt} Me siento {tokenizer.mask_token}.", top_k=TOP_K)
    emotions_with_scores = {}
    for result in results:
        emotions_with_scores[result['token_str']] = float(result['score'])
    return AnalyzePromptResponse(emotions=emotions_with_scores,
                                 dominant_emotion=results[0]['token_str'])


def make_new_prediction(tokenizer, pipeline, prompt: str, session: SessionDep, TOP_K:int = 5):
    text_hash = compute_text_hash(prompt)
    prompt_analysis = look_up_query(text_hash, session)
    if prompt_analysis is not None:
        return AnalyzePromptResponse(emotions=prompt_analysis.emotions,
                                     dominant_emotion=prompt_analysis.dominant_emotion)
    else:
        result = get_emotional_analysis(tokenizer, pipeline, prompt, TOP_K)
        store_query(text_hash, result, session)
        return result