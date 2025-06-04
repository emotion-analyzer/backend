from transformers import AutoModelForMaskedLM, AutoTokenizer, pipeline

from analyzer.config import config


def load_emotions_model():
    """Load model, tokenizer and prepare an MLM pipeline for emotion analysis."""
    tokenizer = AutoTokenizer.from_pretrained(config.HUGGING_FACE.MODEL_URL)
    model = AutoModelForMaskedLM.from_pretrained(config.HUGGING_FACE.MODEL_URL)
    fill_mask = pipeline("fill-mask", model=model, tokenizer=tokenizer, device="cpu")
    return tokenizer, fill_mask
