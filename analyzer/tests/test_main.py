# ruff: noqa: E501, D103
import sys
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel

from analyzer.database.session import create_db_and_tables, engine

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

@patch('analyzer.main.load_emotions_model')
def test_01_successful_user_registration_returns_422(client):
    response = client.post("/register", json=valid_user_1)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "message": "Usuario registrado exitosamente",
    }
