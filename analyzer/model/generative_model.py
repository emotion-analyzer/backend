from dataclasses import dataclass
import gc

import torch
from transformers import AutoModelForSeq2SeqLM

from analyzer.core.exceptions import ModelConfigurationError
from analyzer.core.metrics import emotional_analysis_duration
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

    def process_batch(self, texts: list[str], batch_size: int = 10) -> list[dict[str, float]]:
        if not texts:
            return []

        self._tokenizer.padding_side = "left"
        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token

        all_batch_results = []

        for i in range(0, len(texts), batch_size):
            chunk = texts[i:i + batch_size]
            formatted_chunk = [f"{text}. Me siento <extra_id_0>" for text in chunk]

            inputs = self._tokenizer(
                formatted_chunk,
                truncation=True,
                padding=True,
                return_tensors="pt"
            ).to(self._device)

            try:
                with torch.no_grad():
                    output = self._model.generate(
                        **inputs,
                        num_beams=5,
                        num_return_sequences=5,
                        max_new_tokens=5,
                        early_stopping=True,
                        return_dict_in_generate=True,
                        output_scores=True
                    )

                current_batch_size = len(chunk)
                probs = torch.exp(output.sequences_scores).view(current_batch_size, 5)
                sequences = output.sequences.view(current_batch_size, 5, -1)

                for b in range(current_batch_size):
                    item_results = {}
                    for s in range(5):
                        seq = sequences[b, s]
                        p = probs[b, s].item()
                        decoded = self._tokenizer.decode(seq, skip_special_tokens=True).strip()
                        if decoded:
                            t = decoded.split()[0]
                            if t in self._affective_states and '.' not in t:
                                item_results[t] = p
                    all_batch_results.append({t: p for t, p in item_results.items() if p >= self.threshold})

            except torch.OutOfMemoryError:
                self._logger.warning(f"GPU OOM")
                all_batch_results.extend([{} for _ in chunk])
                torch.cuda.empty_cache()
                gc.collect()
            finally:
                del inputs
                torch.cuda.empty_cache()

        return all_batch_results


