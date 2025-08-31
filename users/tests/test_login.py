from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND

from users.core.security import decode_token
from users.database.session import create_db_and_tables, engine
from users.main import app
from users.tests.test_constants import (
    valid_user_1,
    valid_user_2,
    valid_user_3,
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


def test_valid_log_in_response_returns_correct_fields(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert "user" in response.json()


def test_valid_log_in_response_returns_correct_user_details(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    user = response.json()["user"]
    assert 1 == user["id"]
    assert valid_user_1["email"] == user["email"]
    assert valid_user_1["username"] == user["username"]
    assert valid_user_1["username"] == user["display_name"]
    assert user["avatar_url"] is None


def test_valid_log_in_token_contains_correct_data(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    assert response.json()["token_type"] == "bearer"
    decoded_token = decode_token(response.json()["access_token"])
    assert valid_user_1["email"] == decoded_token["email"]


def test_logging_in_with_nonexistent_user_returns_404(client):
    client.post("/register", json=valid_user_1)
    user_2_login = {k: v for k, v in valid_user_2.items() if k != "username"}
    response = client.post("/login", json=user_2_login)
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Usuario no encontrado."}


def test_logging_in_with_incorrect_password_returns_401(client):
    client.post("/register", json=valid_user_3)
    user_3_login = {k: v for k, v in valid_user_3.items() if k != "username"}
    user_3_login["password"] = "invalid_pw"
    response = client.post("/login", json=user_3_login)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Contraseña invalida."}
