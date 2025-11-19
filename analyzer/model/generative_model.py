from dataclasses import dataclass
import gc

import torch
from transformers import AutoModelForSeq2SeqLM

from analyzer.core.exceptions import ModelConfigurationError
from analyzer.model.base_model import EmotionAnalyzerModel


@dataclass
class GenerativeModel(EmotionAnalyzerModel):
    """Masked language model base class."""
    def __init__(self, url, threshold, affective_states, logger):
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            self._model = AutoModelForSeq2SeqLM.from_pretrained(url).to(self._device)
        except OSError:
            logger.warning(f"Generative model {url} not recognized as valid. Skipping...")
            raise ModelConfigurationError() from None
        if affective_states is None:
            logger.warning(f"Affective state list for {url} not found. Skipping...")
            raise ModelConfigurationError()
        if self._device =="cpu":
            logger.warning("Model is running on CPU.")
        self._model.eval()
        self._affective_states = affective_states
        super().__init__(url, threshold, logger)
        self._logger.info(f"Generative model succesfully loaded. Name: {url}, "
                          f"threshold: {threshold}")

    def process(self, text) -> dict[str, float]:
        """Analyze text and return a dictionary of affective states with their scores."""
        text = f"{text}. Me siento <extra_id_0>"
        inputs = self._tokenizer(text, truncation=True, return_tensors="pt")
        inputs = {k: v.to(self._device) for k, v in inputs.items()}
        results = {}
        try:
            with torch.no_grad():
                output = self._model.generate(
                    **inputs,
                    num_beams=5,
                    num_return_sequences=5,
                    max_new_tokens=10,
                    early_stopping=True,
                    return_dict_in_generate=True,
                    output_scores=True
                )
            probs = torch.exp(output.sequences_scores)
            texts = [self._tokenizer.decode(seq, skip_special_tokens=True).split()[0]
                     for seq in output.sequences]
            tuples = zip(texts, probs, strict=False)
            results = {t: p.item() for t, p in tuples if t in self._affective_states}
            results = {k: v for k, v in results.items() if '.' not in k}
            del output, probs, texts
            del inputs
        except torch.OutOfMemoryError:
            self._logger.warning("CUDA out of memory. Clearing memory...")
            gc.collect()
        finally:
            torch.cuda.empty_cache()
        return results


