from dataclasses import dataclass

from transformers import AutoModelForSequenceClassification, pipeline

from analyzer.model.base_model import EmotionAnalyzerModel


@dataclass
class ClassificationModel(EmotionAnalyzerModel):
    """Masked language model base class."""
    def __init__(self, url, threshold):
        self._model = AutoModelForSequenceClassification.from_pretrained(url)
        self._model.eval()
        super().__init__(url, threshold)
        self._pipeline = pipeline("text-classification", model=self._model,
                                  tokenizer=self._tokenizer, truncation=True,
                                  padding=True, max_length=512, top_k=10)


    def process(self, text) -> dict[str, float]:
        """Analyze text and return a dictionary of affective states with their scores."""
        results = self._pipeline(text)[0]
        results_dict = {r["label"]: float(r["score"]) for r in results[:5]}
        return results_dict
