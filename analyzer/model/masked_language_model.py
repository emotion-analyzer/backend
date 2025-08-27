# ruff: noqa: E501
from dataclasses import dataclass

import torch
from torch.nn.functional import softmax
from transformers import AutoModelForMaskedLM

from analyzer.config import config
from analyzer.model.base_model import EmotionAnalyzerModel


@dataclass
class MaskedLanguageModel(EmotionAnalyzerModel):
    """Masked language model base class."""
    def __init__(self, url, threshold):
        self._model = AutoModelForMaskedLM.from_pretrained(url)
        super().__init__(url, threshold)

    def process(self, text) -> dict[str, float]:
        """Pass prompt through model and get specified number of top predictions."""
        full_text = f"{text}. Me siento {self._tokenizer.mask_token}."

        # Tokenize + truncate from front
        ids = self._tokenizer(full_text, add_special_tokens=True, return_tensors="pt")["input_ids"]
        trunc_ids = ids[:, -self._tokenizer.model_max_length:]

        # Get model output
        with torch.no_grad():
            outputs = self._model(input_ids=trunc_ids)
            token_id = self._tokenizer.mask_token_id
            mask_idx = (trunc_ids == token_id).nonzero(as_tuple=True)[1].item()
            logits = outputs.logits[0, mask_idx]
            topk = torch.topk(logits, config.MODEL.TOP_K)

        # Convert logits to probabilities
        probs = softmax(topk.values, dim=0)

        # Format results like pipeline
        affective_states = {}

        for token_id, score in zip(topk.indices, probs, strict=False):
            token_str = self._tokenizer.decode([token_id])
            sequence_ids = trunc_ids.clone()
            sequence_ids[0, mask_idx] = token_id
            # sequence = tokenizer.decode(sequence_ids[0], skip_special_tokens=True)
            if score.item() >= config.MODEL.THRESHOLD:
                affective_states[token_str] = float(score.item())
            else:
                break

        if len(affective_states) == 0:
            affective_states["neutral"] = 1

        return affective_states
