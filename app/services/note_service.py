import math
from sqlmodel import Session, col, func, or_, select
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteList, NoteQuery, NoteResponse, NoteUpsert


def get_all_user_notes(db: Session, query: NoteQuery, user: User) -> NoteList:
    page = query.page
    page_size = query.page_size
    q = query.q

    statement = select(Note).where(Note.user_id == user.id)

    if q:
        statement = statement.where(
            or_(
                col(Note.title).ilike(f"%{q}%"),
                col(Note.content).ilike(f"%{q}%"),
            )
        )

    notes = db.exec(statement.offset((page - 1) * page_size).limit(page_size)).all()

    total = db.exec(select(func.count()).select_from(statement)).one()

    return NoteList(
        data=[NoteResponse.model_validate(n) for n in notes],
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": math.ceil(total / page_size),
        },
    )


def create_note(db: Session, note: NoteUpsert, user: User) -> Note:
    db_note = Note(
        title=note.title,
        content=note.content,
        user_id=user.id,
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def update_note(db: Session, existing_note: Note, note: NoteUpsert) -> Note:
    existing_note.title = note.title
    existing_note.content = note.content
    db.commit()
    db.refresh(existing_note)
    return existing_note


def delete_note(db: Session, existing_note: Note) -> None:
    db.delete(existing_note)
    db.commit()
