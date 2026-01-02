from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.note import Note
from app.models.user import User


def get_owned_note(
    note_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Note:
    statement = select(Note).where(Note.id == note_id)
    note = db.exec(statement).first()

    if not note:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if note.user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return note
