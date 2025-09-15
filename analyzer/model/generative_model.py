from dataclasses import dataclass

import torch
from transformers import AutoModelForSeq2SeqLM

from analyzer.model.base_model import EmotionAnalyzerModel


@dataclass
class GenerativeModel(EmotionAnalyzerModel):
    """Masked language model base class."""
    def __init__(self, url, threshold):
        self._model = AutoModelForSeq2SeqLM.from_pretrained(url)
        self._model.eval()
        super().__init__(url, threshold)

    def process(self, text) -> dict[str, float]:
        """Analyze text and return a dictionary of affective states with their scores."""
        text = f"{text}. Me siento"
        inputs = self._tokenizer(text, return_tensors="pt")
        output = self._model.generate(
            **inputs,
            num_beams=5,
            num_return_sequences=5,
            max_new_tokens=20,
            early_stopping=True,
            return_dict_in_generate=True,
            output_scores=True
        )
        probs = torch.exp(output.sequences_scores)
        texts = [self._tokenizer.decode(seq, skip_special_tokens=True)
                 for seq in output.sequences]
        results = {t: p.item() for t, p in zip(texts, probs, strict=False)}
        return results

