from typing import Iterator
from sqlmodel import Session
from app.core.database import SessionLocal


def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
