from analyzer.core.schemas import AnalyzePromptResponse


def make_new_prediction(tokenizer, pipeline, prompt: str, TOP_K:int = 5):
    results = pipeline(f"{prompt} Me siento {tokenizer.mask_token}.", top_k=TOP_K)
    emotions_with_scores = {}
    for result in results:
        emotions_with_scores[result['token_str']] = float(result['score'])
    return AnalyzePromptResponse(emotions=emotions_with_scores,
                                 dominant_emotion=results[0]['token_str'])