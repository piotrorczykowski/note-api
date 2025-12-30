from sqlmodel import Field, Relationship, SQLModel

from app.models.base import AuditMixin


class User(AuditMixin, SQLModel, table=True):
    __tablename__: str = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    full_name: str
    password: str

    notes: list["Note"] = Relationship(back_populates="user")  # type: ignore # noqa: F821
