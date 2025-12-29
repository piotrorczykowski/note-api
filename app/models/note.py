from sqlmodel import Field, SQLModel
from app.models.base import AuditMixin


class Note(AuditMixin, SQLModel, table=True):
    __tablename__: str = "notes"

    id: int | None = Field(default=None, primary_key=True)
    title: str | None
    content: str
