from analyzer.config import config
from analyzer.model.classification_model import ClassificationModel
from analyzer.model.generative_model import GenerativeModel


def load_affective_states(filename: str):
    """Load affective states file for generative model sanitization."""
    try:
        with open(f"analyzer/model/{filename}") as f:
            affective_states = set(line.strip() for line in f)
            return affective_states
    except FileNotFoundError:
        return None

def load_generative_model(loaded_models, model_name: str,
                          affective_states: set[str], logger):
    """Load generative model with specified name and affective states."""
    loaded_models[model_name] = (
        GenerativeModel(
            url=f"{config.HUGGING_FACE.REPO}/{model_name}_model",
            threshold=config.MODEL.GENERATIVE_THRESHOLD,
            affective_states=affective_states,
            logger=logger))

def load_classification_model(loaded_models, model_name: str, logger):
    """Load classification model with specified name."""
    loaded_models[model_name] = (
        ClassificationModel(
            url=f"{config.HUGGING_FACE.REPO}/{model_name}_model",
            threshold=config.MODEL.CLASSIFICATION_THRESHOLD,
            logger=logger))

def load_models(logger):
    """Load latest versions of all trained emotions models."""
    models = config.HUGGING_FACE.MODELS.split(",")
    loaded_models = {}
    es_affective_states = load_affective_states("affective_states_es.txt",)
    en_affective_states = load_affective_states("affective_states_es.txt")
    for model in models:
        if model == "all":
            load_classification_model(models, "es_classification", logger)
            load_classification_model(models, "en_classification", logger)
            load_generative_model(models, "es_generative", es_affective_states, logger)
            load_generative_model(models, "en_generative", en_affective_states, logger)
        else:
            if model == "es_classification":
                load_classification_model(loaded_models, model, logger)
            if model == "en_classification":
                load_classification_model(loaded_models, model, logger)
            if model == "es_generative":
                load_generative_model(loaded_models, model, es_affective_states, logger)
            if model == "en_generative":
                load_generative_model(loaded_models, model, en_affective_states, logger)
    return loaded_models
