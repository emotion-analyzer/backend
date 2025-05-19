# ruff: noqa: E501, D103

from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel

from users.core.security import decode_token
from users.database.session import create_db_and_tables, engine
from users.main import app
from users.tests.test_constants import (
    invalid_user,
    repeated_email_user_1,
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


def test_01_successful_user_registration_returns_200(client):
    response = client.post("/register", json=valid_user_1)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "message": "Usuario registrado exitosamente",
    }


def test_02_missing_details_user_registration_returns_422(client):
    response = client.post("/register", json=invalid_user)
    assert response.status_code == 422


def test_03_repeated_username_registration_returns_409(client):
    client.post("register", json=valid_user_1)
    response = client.post("register", json=valid_user_1)
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Usuario ya registrado con este nombre de usuario."
    }


def test_04_several_users_registered_with_different_details_return_correct_ids(
    client,
):
    response_1 = client.post("/register", json=valid_user_1)
    response_2 = client.post("/register", json=valid_user_2)
    response_3 = client.post("/register", json=valid_user_3)
    assert response_1.json() == {
        "id": 1,
        "message": "Usuario registrado exitosamente",
    }
    assert response_2.json() == {
        "id": 2,
        "message": "Usuario registrado exitosamente",
    }
    assert response_3.json() == {
        "id": 3,
        "message": "Usuario registrado exitosamente",
    }


def test_05_repeated_email_registration_returns_409(client):
    client.post("/register", json=valid_user_1)
    response = client.post("/register", json=repeated_email_user_1)
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Usuario ya registrado con este email."
    }


def test_06_logging_in_with_valid_data_returns_200(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    assert response.status_code == 200
    # Again, just a placeholder
    decoded_token = decode_token(response.json()["access_token"])
    assert valid_user_1["email"] == decoded_token["email"]


def test_07_logging_in_with_nonexistent_user_returns_401(client):
    client.post("/register", json=valid_user_1)
    user_2_login = {k: v for k, v in valid_user_2.items() if k != "username"}
    response = client.post("/login", json=user_2_login)
    assert response.status_code == 401
    assert response.json() == {"detail": "Usuario no encontrado."}


def test_08_logging_in_with_incorrect_password_returns_401(client):
    client.post("/register", json=valid_user_3)
    user_3_login = {k: v for k, v in valid_user_3.items() if k != "username"}
    user_3_login["password"] = "invalid_pw"
    response = client.post("/login", json=user_3_login)
    assert response.status_code == 401
    assert response.json() == {"detail": "Contraseña invalida."}


def test_09_deleting_user_without_jwt_returns_401(client):
    response = client.delete("/1")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_10_deleting_user_with_invalid_jwt_format_returns_401(client):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.delete("/1", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Token de seguridad invalido."}


def test_11_deleting_user_with_valid_jwt_but_incorrect_id_returns_401(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/2", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "ID de usuario no coincide."}


def test_12_deleting_user_with_valid_jwt_and_correct_id_returns_200(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/1", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"detail": "Usuario borrado exitosamente."}


def test_13_deleting_user_with_valid_jwt_and_correct_id_twice_returns_404(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.delete("/1", headers=headers)
    response = client.delete("/1", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Usuario no encontrado."}
