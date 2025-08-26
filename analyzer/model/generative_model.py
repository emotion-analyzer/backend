from dataclasses import dataclass

from transformers import AutoModelForSeq2SeqLM

from analyzer.model.base_model import EmotionAnalyzerModel


@dataclass
class GenerativeModel(EmotionAnalyzerModel):
    """Masked language model base class."""
    def __init__(self, url, threshold):
        self._model = AutoModelForSeq2SeqLM.from_pretrained(url)
        super().__init__(url, threshold)

    def process(self, text) -> dict[str, float]:
        """Analyze text and return a dictionary of affective states with their scores."""
        pass
