from abc import abstractmethod
from dataclasses import dataclass

from huggingface_hub import model_info
from transformers import AutoTokenizer


@dataclass
class EmotionAnalyzerModel:
    """Analyzer model base class."""
    def __init__(self, url, threshold, logger):
        self.threshold = threshold
        self._tokenizer = AutoTokenizer.from_pretrained(url)
        self._logger = logger
        self._version = model_info(url).card_data.get("model_version")

    @abstractmethod
    def process(self, text) -> dict[str, float]:
        """Analyze text and return a dictionary of affective states with their scores."""

    def get_version(self) -> str:
       """Return model version or unknown if theres none."""
       if self._version is not None:
           return self._version
       else:
           return "unknown"
