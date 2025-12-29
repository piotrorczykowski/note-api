import math
from sqlmodel import Session, col, func, or_, select
from app.models.note import Note
from app.schemas.note import NoteQuery, NoteUpsert


def get_all_notes(db: Session, query: NoteQuery):
    page = query.page
    page_size = query.page_size
    q = query.q

    statement = select(Note)

    if q:
        statement = statement.where(
            or_(
                col(Note.title).ilike(f"%{q}%"),
                col(Note.content).ilike(f"%{q}%"),
            )
        )

    notes = db.exec(statement.offset((page - 1) * page_size).limit(page_size)).all()

    total = db.exec(select(func.count()).select_from(statement)).one()

    return {
        "data": notes,
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": math.ceil(total / page_size),
        },
    }


def create_note(db: Session, note: NoteUpsert) -> Note:
    db_note = Note(
        title=note.title,
        content=note.content,
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def update_note(db: Session, note_id: int, note: NoteUpsert) -> Note | None:
    statement = select(Note).where(Note.id == note_id)
    db_note = db.exec(statement).first()
    if not db_note:
        return None

    db_note.title = note.title
    db_note.content = note.content
    db.commit()
    db.refresh(db_note)
    return db_note


def delete_note(db: Session, note_id: int) -> None:
    statement = select(Note).where(Note.id == note_id)
    note = db.exec(statement).first()
    if note:
        db.delete(note)
        db.commit()
