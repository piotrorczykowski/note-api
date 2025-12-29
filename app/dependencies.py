from typing import Iterator
from sqlmodel import Session
from app.core.database import engine


def get_db() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
