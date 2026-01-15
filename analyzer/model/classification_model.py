from dataclasses import dataclass

import torch
from transformers import AutoModelForSequenceClassification, pipeline

from analyzer.core.exceptions import ModelConfigurationError
from analyzer.core.metrics import emotional_analysis_duration
from analyzer.model.base_model import EmotionAnalyzerModel


@dataclass
class ClassificationModel(EmotionAnalyzerModel):
    """Masked language model base class."""
    def __init__(self, url, threshold, logger):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            self._model = AutoModelForSequenceClassification.from_pretrained(url)
        except OSError:
            logger.warning(f"Classification model {url} not recognized as valid.")
            raise ModelConfigurationError() from None
        if device =="cpu":
            logger.warning("Model is running on CPU.")
        self._model.eval()
        super().__init__(url, threshold, logger)
        self._pipeline = pipeline("text-classification", device=device, model=self._model,
                                  tokenizer=self._tokenizer, truncation=True,
                                  padding=True, max_length=512, top_k=10)
        self._logger.info(f"Classification model succesfully loaded. Name: {url}, "
                          f"threshold: {threshold}")


    def process(self, text) -> dict[str, float]:
        """Analyze text and return a dictionary of affective states with their scores."""
        with emotional_analysis_duration.labels(model='classification').time():
            results = self._pipeline(text)[0]
            results_dict = {r["label"]: float(r["score"])
                            for r in results[:5] if r["score"] >= self.threshold}
        return results_dict
