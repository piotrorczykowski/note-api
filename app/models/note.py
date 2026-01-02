from sqlmodel import Field, Relationship, SQLModel
from app.models.base import AuditMixin
from app.models.user import User


class Note(AuditMixin, SQLModel, table=True):
    __tablename__: str = "notes"

    id: int | None = Field(default=None, primary_key=True)
    title: str | None
    content: str

    user_id: int = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="notes")
