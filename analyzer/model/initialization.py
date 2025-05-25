from transformers import AutoTokenizer, AutoModelForMaskedLM
from analyzer.config import config

def load_emotions_model():
    tokenizer = AutoTokenizer.from_pretrained(config.HUGGING_FACE.MODEL_URL)
    model = AutoModelForMaskedLM.from_pretrained(config.HUGGING_FACE.MODEL_URL)
    model.eval()
    return tokenizer, model