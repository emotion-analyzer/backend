from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND

from users.database.session import create_db_and_tables, engine
from users.main import app
from users.tests.test_constants import (
    valid_user_1,
)


@pytest.fixture(autouse=True)
def client():
    create_db_and_tables()
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def truncate_tables():
    with Session(engine) as session:
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()

def test_deleting_user_without_jwt_returns_401(client):
    response = client.delete("/me")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_deleting_user_with_invalid_jwt_format_returns_401(client):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.delete("/me", headers=headers)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Token de seguridad invalido."}


def test_deleting_user_with_valid_jwt_and_correct_id_returns_200(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/me", headers=headers)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"detail": "Usuario borrado exitosamente."}


def test_deleting_user_with_valid_jwt_and_correct_id_twice_returns_404(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.delete("/me", headers=headers)
    response = client.delete("/me", headers=headers)
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Usuario no encontrado."}
