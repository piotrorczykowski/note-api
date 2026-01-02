from fastapi import APIRouter, status
from fastapi.params import Depends
from sqlmodel import Session
from app.dependencies import get_db, get_current_user
from app.dependencies.note import get_owned_note
from app.models.note import Note
from app.models.user import User
from app.schemas.error import ErrorResponse
from app.schemas.note import NoteQuery, NoteUpsert, NoteList, NoteResponse
from app.services.note_service import (
    create_note,
    delete_note,
    get_all_user_notes,
    update_note,
)


router = APIRouter(prefix="/notes", tags=["Note"])


@router.get(
    "",
    summary="Get all notes",
    response_description="List of notes",
    response_model=NoteList,
)
def get_all(
    query: NoteQuery = Depends(),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> NoteList:
    return get_all_user_notes(db, query, user)


@router.post(
    "",
    summary="Create a new note",
    response_description="The created note",
    status_code=status.HTTP_201_CREATED,
    response_model=NoteResponse,
)
def create(
    note: NoteUpsert,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Note:
    return create_note(db, note, user)


@router.put(
    "/{note_id}",
    summary="Update a note",
    responses={
        200: {"model": NoteResponse, "description": "Note updated successfully"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Note not found"},
    },
    response_model=NoteResponse,
)
def update(
    note: NoteUpsert,
    existing_note: Note = Depends(get_owned_note),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Note:
    return update_note(db, existing_note, note)


@router.delete(
    "/{note_id}",
    summary="Delete a note",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Note deleted successfully"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Note not found"},
    },
)
def delete(
    existing_note: Note = Depends(get_owned_note),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    delete_note(db, existing_note)
