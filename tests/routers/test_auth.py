from typing import Iterator
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from app.core.config import get_settings
from app.dependencies.db import get_db
from app.main import app


@pytest.fixture(autouse=True)
def setup_test_client():
    """Setup test client with dependency overrides."""

    def override_get_db() -> Iterator[MagicMock]:
        yield MagicMock()

    def override_get_settings():
        return MagicMock()

    get_settings.cache_clear()
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = override_get_settings

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Provide test client."""
    return TestClient(app)


def test_sign_in_success(client):
    credentials = {"email": "test@example.com", "password": "securepass"}

    token_response = {"access_token": "fake-jwt-token"}

    with patch("app.routers.auth.sign_in_user") as mock_sign_in:
        mock_sign_in.return_value = token_response

        response = client.post("/auth/sign-in", json=credentials)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == token_response
        mock_sign_in.assert_called_once()


def test_sign_in_failure(client):
    credentials = {"email": "wrong@example.com", "password": "wrongpass"}

    with patch(
        "app.routers.auth.sign_in_user",
        side_effect=Exception("Invalid email or password"),
    ) as mock_sign_in:
        response = client.post("/auth/sign-in", json=credentials)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Invalid email or password"}
        mock_sign_in.assert_called_once()


def test_sign_up_success(client):
    user_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "securepass",
    }
    user_response = {
        "id": 1,
        "email": user_data["email"],
        "full_name": user_data["full_name"],
    }

    with patch("app.routers.auth.sign_up_user") as mock_sign_up:
        mock_sign_up.return_value = {**user_response, "password": "hashedpassword"}

        response = client.post("/auth/sign-up", json=user_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == user_response
        mock_sign_up.assert_called_once()


def test_sign_up_failure(client):
    user_data = {
        "email": "test@example.com",
        "password": "securepass",
    }

    with patch("app.routers.auth.sign_up_user") as mock_sign_up:
        mock_sign_up.return_value = {}

        response = client.post("/auth/sign-up", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json() == {
            "detail": [
                {
                    "type": "missing",
                    "loc": ["body", "full_name"],
                    "msg": "Field required",
                    "input": {"email": "test@example.com", "password": "securepass"},
                }
            ]
        }
        mock_sign_up.assert_not_called()
