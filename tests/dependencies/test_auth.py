import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

import jwt

from app.core.config import Settings
from app.dependencies.auth import get_current_user, JWT_ALGORITHM
from app.models import User


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_settings():
    settings = MagicMock(spec=Settings)
    settings.jwt_secret_key = "testsecret"
    return settings


@pytest.fixture
def valid_token():
    return "fake-token"


@pytest.fixture
def credentials(valid_token):
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=valid_token)


def test_get_current_user_success(mock_db, mock_settings, credentials):
    fake_user = User(id=1, email="test@example.com")  # type: ignore

    with patch("app.dependencies.auth.jwt.decode") as mock_decode:
        mock_decode.return_value = {"user_id": 1}

        mock_db.exec.return_value.one.return_value = fake_user

        user = get_current_user(
            credentials=credentials,
            db=mock_db,
            settings=mock_settings,
        )

        assert user == fake_user
        mock_decode.assert_called_once_with(
            credentials.credentials,
            mock_settings.jwt_secret_key,
            algorithms=[JWT_ALGORITHM],
        )


def test_get_current_user_invalid_token(mock_db, mock_settings, credentials):
    with patch("app.dependencies.auth.jwt.decode") as mock_decode:
        mock_decode.side_effect = jwt.PyJWTError

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, mock_db, mock_settings)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_missing_user_id(mock_db, mock_settings, credentials):
    with patch("app.dependencies.auth.jwt.decode") as mock_decode:
        mock_decode.return_value = {}

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, mock_db, mock_settings)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_user_not_found(mock_db, mock_settings, credentials):
    with patch("app.dependencies.auth.jwt.decode") as mock_decode:
        mock_decode.return_value = {"user_id": 1}

        mock_db.exec.return_value.one.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, mock_db, mock_settings)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
