from transformers import AutoModelForMaskedLM, AutoTokenizer

from analyzer.config import config


def load_emotions_model():
    """Load model, tokenizer and prepare an MLM pipeline for emotion analysis."""
    tokenizer = AutoTokenizer.from_pretrained(config.HUGGING_FACE.MODEL_URL)
    model = AutoModelForMaskedLM.from_pretrained(config.HUGGING_FACE.MODEL_URL)
    return tokenizer, model
