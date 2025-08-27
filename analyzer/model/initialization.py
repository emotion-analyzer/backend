from analyzer.config import config
from analyzer.model.masked_language_model import MaskedLanguageModel


def load_available_models():
    """Load latest versions of all trained emotions models."""
    models = {
        "masked_language": MaskedLanguageModel(url=config.HUGGING_FACE.URL,
                                               threshold=0.40)
    }
    return models
