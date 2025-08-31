from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND

from users.core.schemas import UserDetails
from users.core.security import encode_token
from users.database.session import create_db_and_tables, engine
from users.main import app
from users.tests.test_constants import (
    invalid_password_reset,
    user_1_details_update,
    user_1_email_update,
    user_1_email_update_wrong_pw,
    user_1_pw_update,
    user_1_pw_update_mismatch,
    user_1_updated_login,
    valid_user_1,
    valid_user_2,
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

# cambio de pw

def test_changing_details_with_no_jwt_returns_401(client):
    response = client.patch("/me", json=user_1_details_update)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_changing_details_with_invalid_jwt_format_returns_401(client):
    headers = {"Authorization": "Bearer invalid"}
    response = client.patch("/me", json=user_1_details_update, headers=headers)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Token de seguridad invalido."}


def test_changing_valid_details_with_jwt_returns_new_client_details(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.patch("/me", json=user_1_details_update, headers=headers)
    assert response.json() == UserDetails(
        id = 1,
        username = user_1_details_update["username"],
        display_name = user_1_details_update["display_name"],
        avatar_url = None,
        email = valid_user_1["email"]).model_dump()


def test_changing_pw_with_new_and_confirm_pw_mismatch_returns_401(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.patch("/me", json=user_1_pw_update_mismatch, headers=headers)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Contraseña de confirmación difiere de la nueva."}


def test_after_changing_pw_login_is_possible_with_new_pw(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.patch("/me", json=user_1_pw_update, headers=headers)
    response = client.post("/login", json=user_1_updated_login)
    assert response.status_code == HTTP_200_OK


def test_changing_email_with_wrong_password_returns_401(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.patch("/me", json=user_1_email_update_wrong_pw, headers=headers)
    assert response.json() == {"detail": "Contraseña inválida."}


def test_changing_email_with_right_password_returns_correct_data(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.patch("/me", json=user_1_email_update, headers=headers)
    assert response.json() == UserDetails(
        id = 1,
        username = valid_user_1["username"],
        display_name = valid_user_1["username"],
        avatar_url = None,
        email = user_1_email_update["email"]).model_dump()


def test_changing_password_with_invalid_jwt_format_returns_401(client):
    response = client.post("/reset-password",
                           json = invalid_password_reset)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Token de seguridad invalido."}


def test_changing_password_with_expired_jwt_format_returns_401(client):
    token = encode_token({"email": valid_user_1["email"]}, 0)
    response = client.post("/reset-password",
                           json ={"token": token,
                                  "new_password": valid_user_2["password"]})
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Token de seguridad invalido."}


def test_changing_password_with_valid_jwt_but_invalid_user_return_404(client):
    client.post("/register", json=valid_user_1)
    token = encode_token({"email": valid_user_2["email"]},
                          expiration_time=60)
    response = client.post("/reset-password",
                           json ={"token": token,
                               "new_password": valid_user_2["password"]})
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Usuario no encontrado."}


def test_successful_password_change_invalidates_old_login(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    token = encode_token({"email": valid_user_1["email"]},
                          expiration_time=60)
    client.post("/reset-password",
                json={"token": token,
                    "new_password": valid_user_2["password"]})
    response = client.post("/login", json=user_1_login)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Contraseña invalida."}


def test_can_login_with_new_password_after_password_reset(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    token = encode_token({"email": valid_user_1["email"]},
                          expiration_time=60)
    client.post("/reset-password",
                json={"token": token,
                    "new_password": valid_user_2["password"]})
    user_1_new_login = user_1_login.copy()
    user_1_new_login.update({"password": valid_user_2["password"]})
    response = client.post("/login", json=user_1_new_login)
    assert response.status_code == HTTP_200_OK
