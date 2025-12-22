from sqlmodel import Session, SQLModel, create_engine
from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.db_url)
SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
