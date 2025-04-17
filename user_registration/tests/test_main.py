from fastapi.testclient import TestClient
from backend.user_registration.main import app
from test_constants import valid_user, invalid_user

client = TestClient(app)


def test_01_successful_user_registration():
    response = client.post("/api/users/register", json=valid_user)
    assert response.status_code == 200
    assert response.json() == {"message": "Usuario registrado exitosamente"}

def test_02_missing_details_user_registration():
    response = client.post("/api/users/register", json=invalid_user)
    assert response.status_code == 422