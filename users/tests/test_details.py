from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel
from starlette.status import HTTP_401_UNAUTHORIZED

from users.core.schemas import UserDetails
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


def test_attempting_to_get_details_with_no_token_returns_401(client):
    client.post("/register", json=valid_user_1)
    response = client.get("/me")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"


def test_attempting_to_get_details_with_invalid_token_returns_401(client):
    client.post("/register", json=valid_user_1)
    headers = {"Authorization": "Bearer invalidToken"}
    response = client.get("/me", headers=headers)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Token de seguridad invalido."


def test_registered_user_returns_correct_details(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/me", headers=headers)
    assert response.json() == UserDetails(
        id = 1,
        username = valid_user_1["username"],
        display_name = valid_user_1["username"],
        avatar_url = None,
        email = valid_user_1["email"]).model_dump()
