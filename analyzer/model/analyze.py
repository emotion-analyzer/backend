from collections import Counter
import json

import torch
from torch.nn.functional import softmax

from analyzer.config import config
from analyzer.core.hashing import compute_text_hash
from analyzer.core.schemas import AnalyzePromptResponse
from analyzer.database.crud import look_up_query, store_query
from analyzer.database.session import SessionDep


def process_text(prompt, tokenizer, model, top_k=5):
    full_text = f"{prompt}. Me siento {tokenizer.mask_token}."

    # Tokenize + truncate from front
    ids = tokenizer(full_text, add_special_tokens=True, return_tensors="pt")["input_ids"]
    truncated_ids = ids[:, -tokenizer.model_max_length:]

    # Get model output
    with torch.no_grad():
        outputs = model(input_ids=truncated_ids)
        mask_token_index = (truncated_ids == tokenizer.mask_token_id).nonzero(as_tuple=True)[1].item()
        logits = outputs.logits[0, mask_token_index]
        topk = torch.topk(logits, top_k)

    # Convert logits to probabilities
    probs = softmax(topk.values, dim=0)

    # Format results like pipeline
    results = []

    for token_id, score in zip(topk.indices, probs):
        token_str = tokenizer.decode([token_id])
        sequence_ids = truncated_ids.clone()
        sequence_ids[0, mask_token_index] = token_id
        sequence = tokenizer.decode(sequence_ids[0], skip_special_tokens=True)

        results.append({
            "token": token_id.item(),
            "token_str": token_str,
            "score": score.item(),
            "sequence": sequence
        })

    return results

def get_emotional_analysis(tokenizer, model,
                           prompt: str, top_k:int = 5):
    """Perform an emotional analysis and store it in the database."""
    results = process_text(prompt, tokenizer, model, top_k=top_k)
    emotions_with_scores = {}
    for result in results:
        emotions_with_scores[result['token_str']] = float(result['score'])
    if float(results[0]['score']) > config.MODEL.EMOTION_THRESHOLD:
        dominant_emotion = results[0]['token_str']
    else:
        dominant_emotion = 'neutral'
    return AnalyzePromptResponse(emotions=emotions_with_scores,
                                 dominant_emotion=dominant_emotion)

def analyze_text(tokenizer, pipeline, prompt: str,
                 session: SessionDep, top_k:int = 5):
    """Return stored analysis or process the text and store the result."""
    text_hash = compute_text_hash(prompt)
    prompt_analysis = look_up_query(text_hash, session)
    if prompt_analysis is not None:
        return prompt_analysis
    else:
        prompt_analysis = get_emotional_analysis(tokenizer, pipeline, prompt, top_k)
        store_query(text_hash, prompt_analysis, session)
        return prompt_analysis
