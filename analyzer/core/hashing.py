import hashlib


def compute_text_hash(text: str) -> str:
    """Hash text using SHA256."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
