# ruff: noqa: E501, D103, E402, F401
import sys
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
import pytest
from starlette.status import HTTP_200_OK, HTTP_422_UNPROCESSABLE_ENTITY

from analyzer.tests.testing_constants import (
    analysis_post_1,
    analysis_post_2,
    invalid_batch_prompt_1,
    post_1_affective_states,
    post_1_dominant_affective_state,
    post_2_affective_states,
    post_2_dominant_affective_state,
    single_post_prompt,
    valid_batch_prompt_1,
    valid_post_1,
    valid_post_2,
)


@pytest.fixture(autouse=True)
def client():
    with TestClient(app) as c:
        yield c

# This will do for now but there has to be a better way to avoid these imports
sys.modules['transformers'] = MagicMock()
sys.modules["torch"] = MagicMock()
sys.modules["torch.nn"] = MagicMock()
sys.modules["torch.nn.functional"] = MagicMock()
sys.modules["elasticsearch"] = MagicMock()

from analyzer.main import app


def test_01_prompt_without_texts_field_returns_422(client):
    response = client.post("/batch", json=invalid_batch_prompt_1)
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


@patch('analyzer.model.analyze.process_text')
@patch('analyzer.model.analyze.look_up_query')
def test_02_first_time_analysis_returns_correct_results(lookup_mock: MagicMock,
                                                        analysis_mock: MagicMock,
                                                        client):
    lookup_mock.return_value = None
    analysis_mock.return_value = post_1_affective_states, post_1_dominant_affective_state
    response = client.post("/batch", json=single_post_prompt)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"posts": [analysis_post_1.model_dump()],
                               "affective_states": {'loco': 0.5, 'harto': 0.5},
                               "mapped_summary": {'ira': 1.0}}


@patch('analyzer.model.analyze.process_text')
@patch('analyzer.model.analyze.look_up_query')
def test_03_batch_prompt_with_texts_field_returns_proper_response(lookup_mock: MagicMock,
                                                        analysis_mock: MagicMock,
                                                        client):
    lookup_mock.return_value = None
    analysis_mock.side_effect = [(post_1_affective_states, post_1_dominant_affective_state),
                                 (post_2_affective_states, post_2_dominant_affective_state)]
    response = client.post("/batch", json=valid_batch_prompt_1)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"posts": [analysis_post_1.model_dump(), analysis_post_2.model_dump()],
                               "affective_states": {'loco': 0.25, 'harto': 0.25, 'triste': 0.25, 'cansado': 0.25},
                               "mapped_summary": {'ira': 0.5, 'tristeza': 0.25, 'disgusto': 0.25}}
