# ruff: noqa: E501, D103, E402
import sys
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel

from analyzer.database.session import create_db_and_tables, engine
from analyzer.tests.testing_constants import (
    analysis_response,
    invalid_batch_prompt_1,
    invalid_prompt_1,
    valid_batch_prompt_1,
    valid_prompt_1,
)

# This will do for now but there has to be a better way to avoid the import
sys.modules['transformers'] = MagicMock()

from analyzer.main import app


@pytest.fixture(autouse=True)
def client():
    create_db_and_tables()
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def truncate_tables():
    yield
    with Session(engine) as session:
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()

def test_01_prompt_with_missing_text_field_returns_422(client):
    response = client.post("/text", json=invalid_prompt_1)
    assert response.status_code == 422


@patch('analyzer.model.prediction.look_up_query')
def test_02_single_prompt_with_text_field_returns_proper_response(analysis_mock: MagicMock,
                                                           client):
    analysis_mock.return_value = analysis_response
    response = client.post("/text", json=valid_prompt_1)
    assert response.status_code == 200
    assert response.json() == {"result": {'dominant_emotion': analysis_response.dominant_emotion,
                                          'emotions': analysis_response.emotions}}


def test_03_prompt_without_texts_field_returns_422(client):
    response = client.post("/batch", json=invalid_batch_prompt_1)
    assert response.status_code == 422


@patch('analyzer.model.prediction.look_up_query')
def test_04_batch_prompt_with_texts_field_returns_proper_response(analysis_mock: MagicMock,
                                                           client):
    analysis_mock.return_value = analysis_response
    response = client.post("/batch", json=valid_batch_prompt_1)
    assert response.status_code == 200
    assert response.json() == {"results": [
        {"text": valid_batch_prompt_1["texts"][0],
         "dominant_emotion": analysis_response.dominant_emotion},
        {"text": valid_batch_prompt_1["texts"][1],
         "dominant_emotion": analysis_response.dominant_emotion}
    ]}
