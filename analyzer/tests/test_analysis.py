from datetime import datetime
import logging
import sys
from unittest.mock import MagicMock

from util.codes import POST
from util.schemas import Post, PostAnalysisResult

sys.modules['transformers'] = MagicMock()
sys.modules["torch"] = MagicMock()
sys.modules["torch.nn"] = MagicMock()
sys.modules["torch.nn.functional"] = MagicMock()
sys.modules["elasticsearch"] = MagicMock()

from analyzer.model.analyze import analyze_post
from analyzer.model.classification_model import ClassificationModel
from analyzer.model.initialization import load_models


def test_analysis_returns_properly_formatted_data(monkeypatch):
    affective_states = {
        "emocionado": 0.70,
        "contento": 0.30
    }
    post = Post(query_processor_id="id1", code=POST,
                source="test_source", link="test_link",
                text="test_text", timestamp=datetime.now(), model="classification",
                language="es")
    post_analysis = PostAnalysisResult(**post.model_dump(),
                                       affective_states=affective_states)
    monkeypatch.setattr("analyzer.model.analyze.look_up_query", lambda text_hash, db: None)
    monkeypatch.setattr("analyzer.model.analyze.store_query", lambda text_hash, prompt_analysis, db: None)
    monkeypatch.setattr(ClassificationModel, "process", lambda self, *args, **kwargs: affective_states)
    available_models = load_models()
    assert analyze_post(available_models, None, post) == post_analysis


def test_analysis_is_stored_correctly_for_masked_language_model(monkeypatch):
    affective_states = {
        "emocionado": 0.70,
        "contento": 0.30
    }
    post = Post(query_processor_id="id1", code=POST,
                source="test_source", link="test_link",
                text="test_text", timestamp=datetime.now(), model="classification",
                language="es")
    post_analysis = PostAnalysisResult(**post.model_dump(),
                                       affective_states=affective_states)
    mock_database = {}
    monkeypatch.setattr("analyzer.model.analyze.look_up_query", lambda text_hash, db: mock_database.get(text_hash, None))

    def mock_store(text_hash, analysis, db):
        mock_database[text_hash] = analysis.model_dump()

    monkeypatch.setattr("analyzer.model.analyze.store_query", mock_store)
    monkeypatch.setattr(ClassificationModel, "process", lambda self, *args, **kwargs: affective_states)
    logger = logging.getLogger("affect_pulse")
    available_models = load_models(logger)
    analyze_post(available_models, None, post)
    assert analyze_post(available_models, None, post) == post_analysis


