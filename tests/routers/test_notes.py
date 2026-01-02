from typing import Iterator
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
import pytest
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.dependencies.note import get_owned_note
from app.main import app
from app.models.note import Note
from app.models.user import User


@pytest.fixture(autouse=True)
def setup_test_client():
    """Setup test client with dependency overrides."""

    def override_get_db() -> Iterator[MagicMock]:
        yield MagicMock()

    def override_get_current_user():
        return User(
            id=1,
            email="test@example.com",
            full_name="Test User",
        )  # type: ignore

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Provide test client."""
    return TestClient(app)


def test_get_all_notes_success(client):
    fake_notes = {
        "data": [
            {"id": 1, "title": "Note 1", "content": "Hello"},
            {"id": 2, "title": "Note 2", "content": "World"},
        ],
        "meta": {
            "page": 1,
            "page_size": 10,
            "total": 2,
            "total_pages": 1,
        },
    }

    with patch("app.routers.notes.get_all_user_notes") as mock_get_notes:
        mock_get_notes.return_value = fake_notes

        response = client.get("/notes")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == fake_notes

        mock_get_notes.assert_called_once()
        db_arg, query_arg, user_arg = mock_get_notes.call_args.args

        assert user_arg.email == "test@example.com"
        assert query_arg.page == 1
        assert query_arg.page_size == 10


def test_get_all_notes_with_query_params(client):
    fake_notes = {
        "data": [],
        "meta": {
            "page": 10,
            "page_size": 20,
            "total": 0,
            "total_pages": 0,
        },
    }

    with patch("app.routers.notes.get_all_user_notes") as mock_get_notes:
        mock_get_notes.return_value = fake_notes

        response = client.get(
            "/notes",
            params={
                "page": 10,
                "page_size": 20,
            },
        )

        assert response.status_code == status.HTTP_200_OK

        db_arg, query_arg, user_arg = mock_get_notes.call_args.args
        assert query_arg.page == 10
        assert query_arg.page_size == 20


def test_get_all_notes_requires_auth(client):
    def override_get_current_user():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = client.get("/notes")

    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )


def test_create_note_success(client):
    note_data = {"title": "New Note", "content": "This is a new note."}
    created_note = {
        "id": 1,
        "title": note_data["title"],
        "content": note_data["content"],
    }

    with patch("app.routers.notes.create_note") as mock_create_note:
        mock_create_note.return_value = created_note

        response = client.post("/notes", json=note_data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == created_note

        mock_create_note.assert_called_once()
        db_arg, note_arg, user_arg = mock_create_note.call_args.args

        assert note_arg.title == note_data["title"]
        assert note_arg.content == note_data["content"]
        assert user_arg.id == 1


def test_create_note_requires_auth(client):
    def override_get_current_user():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    app.dependency_overrides[get_current_user] = override_get_current_user

    note_data = {"title": "New Note", "content": "This is a new note."}

    with patch("app.routers.notes.create_note") as mock_create_note:
        response = client.post("/notes", json=note_data)

        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )

        mock_create_note.assert_not_called()


def test_update_note_success(client):
    existing_note = Note(
        id=1,
        title="Old Title",
        content="Old content.",
        user_id=1,
    )
    updated_data = {"title": "Updated Title", "content": "Updated content."}
    updated_note = {
        "id": 1,
        "title": updated_data["title"],
        "content": updated_data["content"],
    }

    app.dependency_overrides[get_owned_note] = lambda: existing_note

    with patch("app.routers.notes.update_note") as mock_update_note:
        mock_update_note.return_value = updated_note

        response = client.put("/notes/1", json=updated_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == updated_note

        mock_update_note.assert_called_once()
        db_arg, existing_note_arg, note_arg = mock_update_note.call_args.args

        assert existing_note_arg.id == existing_note.id
        assert note_arg.title == updated_data["title"]
        assert note_arg.content == updated_data["content"]


def test_update_note_requires_auth(client):
    def override_get_current_user():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    app.dependency_overrides[get_current_user] = override_get_current_user

    updated_data = {"title": "Updated Title", "content": "Updated content."}

    with patch("app.routers.notes.update_note") as mock_update_note:
        response = client.put("/notes/1", json=updated_data)

        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )
        mock_update_note.assert_not_called()


def test_update_note_forbidden(client):
    def override_get_owned_note():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    app.dependency_overrides[get_owned_note] = override_get_owned_note

    updated_data = {"title": "Updated Title", "content": "Updated content."}

    with patch("app.routers.notes.update_note") as mock_update_note:
        response = client.put("/notes/1", json=updated_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        mock_update_note.assert_not_called()


def test_update_note_not_found(client):
    def override_not_found_note():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    app.dependency_overrides[get_owned_note] = override_not_found_note

    updated_data = {"title": "Updated Title", "content": "Updated content."}

    with patch("app.routers.notes.update_note") as mock_update_note:
        response = client.put("/notes/1", json=updated_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        mock_update_note.assert_not_called()


def test_delete_note_success(client):
    existing_note = Note(
        id=1,
        title="Existing Note",
        content="This is an existing note.",
        user_id=1,
    )
    app.dependency_overrides[get_owned_note] = lambda: existing_note

    with patch("app.routers.notes.delete_note") as mock_delete_note:
        response = client.delete("/notes/1")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_delete_note.assert_called_once()


def test_delete_forbidden(client):
    def override_get_owned_note():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    app.dependency_overrides[get_owned_note] = override_get_owned_note

    with patch("app.routers.notes.delete_note") as mock_delete_note:
        response = client.delete("/notes/1")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        mock_delete_note.assert_not_called()


def test_delete_note_not_found(client):
    def override_not_found_note():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )

    app.dependency_overrides[get_owned_note] = override_not_found_note

    with patch("app.routers.notes.delete_note") as mock_delete_note:
        response = client.delete("/notes/1")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        mock_delete_note.assert_not_called()
