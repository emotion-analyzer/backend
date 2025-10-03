from starlette.status import (
    HTTP_200_OK,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_CONTENT,
)

from users.tests.test_constants import (
    invalid_user,
    repeated_email_user_1,
    valid_user_1,
    valid_user_2,
    valid_user_3,
)


def test_successful_user_registration_returns_200_and_user_details(client):
    response = client.post("/register", json=valid_user_1)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "message": "Usuario registrado exitosamente",
    }


def test_missing_details_user_registration_returns_422(client):
    response = client.post("/register", json=invalid_user)
    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


def test_repeated_username_registration_returns_409(client):
    client.post("register", json=valid_user_1)
    response = client.post("register", json=valid_user_1)
    assert response.status_code == HTTP_409_CONFLICT
    assert response.json() == {
        "detail": "Usuario ya registrado con este nombre de usuario."
    }


def test_several_users_registered_with_different_details_return_correct_ids(
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


def test_repeated_email_registration_returns_409(client):
    client.post("/register", json=valid_user_1)
    response = client.post("/register", json=repeated_email_user_1)
    assert response.status_code == HTTP_409_CONFLICT
    assert response.json() == {
        "detail": "Usuario ya registrado con este email."
    }
