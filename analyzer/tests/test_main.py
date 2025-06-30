# ruff: noqa: E501, D103, E402
import sys
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel
from starlette.status import HTTP_200_OK, HTTP_422_UNPROCESSABLE_ENTITY

from analyzer.database.session import create_db_and_tables, engine
from analyzer.tests.testing_constants import (
    analysis_post_1,
    analysis_post_2,
    invalid_batch_prompt_1,
    valid_batch_prompt_1,
)

# This will do for now but there has to be a better way to avoid these imports
sys.modules['transformers'] = MagicMock()
sys.modules["torch"] = MagicMock()
sys.modules["torch.nn"] = MagicMock()
sys.modules["torch.nn.functional"] = MagicMock()

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


def test_01_prompt_without_texts_field_returns_422(client):
    response = client.post("/batch", json=invalid_batch_prompt_1)
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


@patch('analyzer.model.analyze.look_up_query')
def test_02_batch_prompt_with_texts_field_returns_proper_response(analysis_mock: MagicMock,
                                                           client):
    analysis_mock.side_effect = [analysis_post_1, analysis_post_2]
    response = client.post("/batch", json=valid_batch_prompt_1)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"posts": [analysis_post_1.model_dump(), analysis_post_2.model_dump()],
                               "affective_states": {'harto': 0.5, 'triste': 0.5},
                               "mapped_summary": {'ira': 0.5, 'tristeza': 0.5}
                               }
