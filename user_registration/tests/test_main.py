import pytest

from fastapi.testclient import TestClient
from sqlmodel import SQLModel
from user_registration.main import app
from user_registration.tests.test_constants import valid_user_1, invalid_user

from user_registration.database.session import engine


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def reset_database():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

def test_01_successful_user_registration(client):
    response = client.post("/api/users/register", json=valid_user_1)
    assert response.status_code == 200
    assert response.json() == {"id": 1, "message": "Usuario registrado exitosamente"}


def test_02_missing_details_user_registration(client):
    response = client.post("/api/users/register", json=invalid_user)
    assert response.status_code == 422
