from analyzer.config import config
from analyzer.model.classification_model import ClassificationModel
from analyzer.model.generative_model import GenerativeModel


def load_available_models():
    """Load latest versions of all trained emotions models."""
    models = {
        "classification": ClassificationModel(
            url=config.HUGGING_FACE.CLASSIFICATION_MODEL,
            threshold=config.MODEL.THRESHOLD),
        "english": ClassificationModel(
            url=config.HUGGING_FACE.EN_MODEL,
            threshold=config.MODEL.THRESHOLD),
        "generative": GenerativeModel(
            url=config.HUGGING_FACE.GENERATIVE_MODEL,
            threshold=config.MODEL.THRESHOLD)
    }
    return models
