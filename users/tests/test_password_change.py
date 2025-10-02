from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from users.tests.test_constants import (
    user_1_pw_update,
    user_1_pw_update_mismatch,
    user_1_updated_login,
    valid_user_1,
)


def test_changing_details_with_no_jwt_returns_401(client):
    response = client.post("/me/change-password", json=user_1_pw_update)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_changing_details_with_invalid_jwt_format_returns_401(client):
    headers = {"Authorization": "Bearer invalid"}
    response = client.post("/me/change-password", json=user_1_pw_update, headers=headers)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Token de seguridad invalido."}


def test_changing_password_with_valid_jwt_but_wrong_password_returns_401(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/me/change-password", json=user_1_pw_update_mismatch, headers=headers)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Contraseña inválida.'}


def test_after_changing_pw_login_is_possible_with_new_pw(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/me/change-password", json=user_1_pw_update, headers=headers)
    response = client.post("/login", json=user_1_updated_login)
    assert response.status_code == HTTP_200_OK


def test_after_changing_pw_login_with_old_password_returns_401(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    response = client.post("/login", json=user_1_login)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/me/change-password", json=user_1_pw_update, headers=headers)
    response = client.post("/login", json=user_1_login)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Contraseña inválida.'}
