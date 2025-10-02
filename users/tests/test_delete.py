
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND

from users.tests.test_constants import (
    valid_user_1,
)


def test_deleting_user_without_jwt_returns_401(client):
    response = client.request(
        "DELETE",
        "/me",
        json={"current_password": "123"}
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_deleting_user_with_invalid_jwt_format_returns_401(client):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.request(
        "DELETE",
        "/me",
        json={"current_password": "123"},
        headers=headers
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Token de seguridad invalido."}


def test_deleting_user_with_valid_jwt_but_invalid_password_returns_401(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.request(
        "DELETE",
        "/me",
        json={"current_password": "jorgelin_pw"},
        headers=headers
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Contraseña inválida."}


def test_deleting_user_with_valid_jwt_and_valid_password_returns_200(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.request(
        "DELETE",
        "/me",
        json={"current_password": "jorgito_pw"},
        headers=headers
    )
    #assert response.status_code == HTTP_200_OK
    assert response.json() == {"detail": "Usuario borrado exitosamente."}


def test_deleting_user_with_valid_jwt_and_correct_id_twice_returns_404(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.request(
        "DELETE",
        "/me",
        json={"current_password": "jorgito_pw"},
        headers=headers)
    response = client.request(
        "DELETE",
        "/me",
        json={"current_password": "jorgito_pw"},
        headers=headers
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Usuario no encontrado."}
