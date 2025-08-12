
import torch
from torch.nn.functional import softmax

from analyzer.config import config
from analyzer.core.hashing import compute_text_hash
from analyzer.core.schemas import Post, PostAnalysisResult
from analyzer.result_storage.crud import look_up_query, store_query


def process_text(tokenizer, model, prompt):
    """Pass prompt through model and get specified number of top predictions."""
    full_text = f"{prompt}. Me siento {tokenizer.mask_token}."

    # Tokenize + truncate from front
    ids = tokenizer(full_text, add_special_tokens=True, return_tensors="pt")["input_ids"]
    trunc_ids = ids[:, -tokenizer.model_max_length:]

    # Get model output
    with torch.no_grad():
        outputs = model(input_ids=trunc_ids)
        mask_idx = (trunc_ids == tokenizer.mask_token_id).nonzero(as_tuple=True)[1].item()
        logits = outputs.logits[0, mask_idx]
        topk = torch.topk(logits, config.MODEL.TOP_K)

    # Convert logits to probabilities
    probs = softmax(topk.values, dim=0)

    # Format results like pipeline
    affective_states = {}
    dominant_affective_state = "neutral"

    for token_id, score in zip(topk.indices, probs, strict=False):
        token_str = tokenizer.decode([token_id])
        sequence_ids = trunc_ids.clone()
        sequence_ids[0, mask_idx] = token_id
        #sequence = tokenizer.decode(sequence_ids[0], skip_special_tokens=True)
        if score.item() >= config.MODEL.THRESHOLD:
            if dominant_affective_state == "neutral":
                dominant_affective_state = token_str
            affective_states[token_str] = float(score.item())
        else:
            break

    return affective_states, dominant_affective_state

def analyze_post(tokenizer, pipeline, db, post: Post):
    """Return stored affective state analysis or process and store the result."""
    text_hash = compute_text_hash(post.text)
    prompt_analysis = look_up_query(text_hash, db)
    if prompt_analysis is None:
        affective_states, dominant_affective_state = process_text(tokenizer,
                                                                  pipeline,
                                                                  post)
        prompt_analysis = PostAnalysisResult(**post.model_dump(),
                                           affective_states=affective_states,
                                           dominant_affective_state=dominant_affective_state)
        store_query(text_hash,prompt_analysis, db)
    else:
        prompt_analysis = PostAnalysisResult(**prompt_analysis)
    return prompt_analysis
