import torch
import torch.nn.functional as functional

from analyzer.core.schemas import AnalyzePromptResponse


def make_new_prediction(tokenizer, model, prompt: str, TOP_K:int = 5):
    text = f"{prompt} Me siento {tokenizer.mask_token}."

    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)

    # Find the position of the mask token
    mask_token_index = (inputs.input_ids == tokenizer.mask_token_id)[0].nonzero(as_tuple=True)[0]

    # Get logits at the mask position
    logits = outputs.logits[0, mask_token_index, :]

    # Get top-k token IDs and their scores
    top_k_values, top_k_indices = torch.topk(logits, TOP_K, dim=-1)
    top_k_values = functional.softmax(top_k_values, dim=-1)

    emotions_with_scores = {}

    for i, token_ids in enumerate(top_k_indices):
        for score, token_id in zip(top_k_values[i], token_ids):
            token = tokenizer.decode([token_id.item()])
            emotions_with_scores[token] = score.item()

    return AnalyzePromptResponse(emotions=emotions_with_scores,
                                 dominant_emotion=tokenizer.decode(top_k_indices[0][0]))