from abc import abstractmethod
from dataclasses import dataclass

from transformers import AutoTokenizer


@dataclass
class EmotionAnalyzerModel:
    """Analyzer model base class."""
    def __init__(self, url, threshold):
        self.threshold = threshold
        self._tokenizer = AutoTokenizer.from_pretrained(url)


    @abstractmethod
    def process(self, text) -> dict[str, float]:
        """Analyze text and return a dictionary of affective states with their scores."""
