import torch

from analyzer.core.schemas import AnalyzePrompt

def make_new_prediction(tokenizer, model, prompt: AnalyzePrompt, TOP_K:int = 5):
    text = f"{prompt.text} Me siento {tokenizer.mask_token}."

    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)

    # Find the position of the mask token
    mask_token_index = (inputs.input_ids == tokenizer.mask_token_id)[0].nonzero(as_tuple=True)[0]

    # Get logits at the mask position
    logits = outputs.logits[0, mask_token_index, :]

    # Get top-k token IDs and their scores
    top_k_values, top_k_indices = torch.topk(logits, TOP_K, dim=-1)

    print(f"Input: {text}")
    for i, token_ids in enumerate(top_k_indices):
        print(f"\nPredictions for mask #{i+1}:")
        for score, token_id in zip(top_k_values[i], token_ids):
            token = tokenizer.decode([token_id.item()])
            print(f"{token} (score: {score.item():.4f})")
    print("\n")