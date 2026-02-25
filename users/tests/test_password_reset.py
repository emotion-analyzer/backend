from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND

from users.core.security import encode_token
from users.tests.test_constants import (
    valid_user_1,
    valid_user_2,
)


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
    token = encode_token({"email": valid_user_1["email"], "id": 1},
                          expiration_time=60)
    client.post("/reset-password",
                json={"token": token,
                    "new_password": valid_user_2["password"]})
    response = client.post("/login", json=user_1_login)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Contraseña inválida."}


def test_can_login_with_new_password_after_password_reset(client):
    client.post("/register", json=valid_user_1)
    user_1_login = {k: v for k, v in valid_user_1.items() if k != "username"}
    token = encode_token({"email": valid_user_1["email"], "id": 1},
                          expiration_time=60)
    client.post("/reset-password",
                json={"token": token,
                    "new_password": valid_user_2["password"]})
    user_1_new_login = user_1_login.copy()
    user_1_new_login.update({"password": valid_user_2["password"]})
    response = client.post("/login", json=user_1_new_login)
    assert response.status_code == HTTP_200_OK
