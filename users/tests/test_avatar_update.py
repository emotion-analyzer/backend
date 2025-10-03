from starlette.status import HTTP_401_UNAUTHORIZED


def test_updating_avatar_without_jwt_returns_401(client):
    response = client.put("/me/avatar")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}

