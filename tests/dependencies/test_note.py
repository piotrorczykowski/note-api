import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException, status

from app.dependencies.note import get_owned_note
from app.models import User, Note


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_user():
    return User(id=1, email="test@example.com")  # type: ignore


def test_get_owned_note_success(mock_db, mock_user):
    note = Note(id=1, title="Test", content="Hello", user_id=mock_user.id)
    mock_db.exec.return_value.first.return_value = note

    result = get_owned_note(note_id=1, db=mock_db, user=mock_user)

    assert result == note

    mock_db.exec.assert_called_once()


def test_get_owned_note_not_found(mock_db, mock_user):
    mock_db.exec.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_owned_note(note_id=1, db=mock_db, user=mock_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_get_owned_note_forbidden(mock_db, mock_user):
    note = Note(id=1, title="Test", content="Hello", user_id=2)
    mock_db.exec.return_value.first.return_value = note

    with pytest.raises(HTTPException) as exc_info:
        get_owned_note(note_id=1, db=mock_db, user=mock_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
