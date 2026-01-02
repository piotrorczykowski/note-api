import pytest
from unittest.mock import MagicMock
from app.models import Note, User
from app.schemas.note import NoteList, NoteQuery, NoteUpsert
from app.services.note_service import (
    create_note,
    get_all_user_notes,
    update_note,
    delete_note,
)


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_user():
    return User(id=1)  # type: ignore


@pytest.fixture
def notes_data(mock_user):
    return [
        Note(id=1, title="Note 1", content="Hello", user_id=mock_user.id),
        Note(id=2, title="Note 2", content="World", user_id=mock_user.id),
    ]


@pytest.fixture
def note_data():
    return NoteUpsert(title="Test Note", content="Hello World")


@pytest.fixture
def existing_note(mock_user):
    return Note(id=1, title="Old Title", content="Old Content", user_id=mock_user.id)


def test_get_all_user_notes_no_query(mock_db, mock_user, notes_data):
    mock_exec = MagicMock()
    mock_exec.all.return_value = notes_data
    mock_exec.offset.return_value = mock_exec
    mock_exec.limit.return_value = mock_exec

    mock_db.exec.return_value = mock_exec
    mock_db.exec.return_value.one.return_value = len(notes_data)

    query = NoteQuery(page=1, page_size=10)

    result = get_all_user_notes(mock_db, query, mock_user)

    assert isinstance(result, NoteList)
    assert len(result.data) == len(notes_data)
    assert result.meta.total == 2
    assert result.meta.page == 1
    assert result.meta.page_size == 10
    assert result.meta.total_pages == 1

    assert mock_db.exec.call_count >= 2


def test_get_all_user_notes_pagination(mock_db, mock_user, notes_data):
    mock_chain = MagicMock()
    mock_chain.all.return_value = [*notes_data, *notes_data]

    mock_chain.offset.return_value = mock_chain
    mock_chain.limit.return_value = mock_chain

    mock_db.exec.return_value = mock_chain
    mock_db.exec.return_value.one.return_value = 4

    query = NoteQuery(page=2, page_size=2)

    result = get_all_user_notes(mock_db, query, mock_user)

    assert result.meta.page == 2
    assert result.meta.page_size == 2
    assert result.meta.total == 4
    assert result.meta.total_pages == 2


def test_create_note_success(mock_db, mock_user, note_data):
    mock_db.refresh.side_effect = lambda x: x

    new_note = create_note(mock_db, note_data, mock_user)

    assert new_note.title == note_data.title
    assert new_note.content == note_data.content
    assert new_note.user_id == mock_user.id

    mock_db.add.assert_called_once_with(new_note)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(new_note)


def test_update_note_success(mock_db, existing_note, note_data):
    mock_db.refresh.side_effect = lambda x: x

    updated_note = update_note(mock_db, existing_note, note_data)

    assert updated_note.title == note_data.title
    assert updated_note.content == note_data.content

    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(existing_note)


def test_delete_note_success(mock_db, existing_note):
    delete_note(mock_db, existing_note)

    mock_db.delete.assert_called_once_with(existing_note)
    mock_db.commit.assert_called_once()
