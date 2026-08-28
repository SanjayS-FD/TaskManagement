import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200


def test_invalid_login():

    response = client.post(
        "/login",
        json={
            "username": "wrong",
            "password": "wrong"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Invalid username"


def test_create_user_without_token():

    response = client.post(
        "/users",
        json={
            "username": "test",
            "email": "test@test.com",
            "password": "123",
            "role": "user"
        }
    )

    assert response.status_code == 401


def test_get_users_without_token():

    response = client.get("/users")

    assert response.status_code == 401


def test_me_without_token():

    response = client.get("/me")

    assert response.status_code == 401