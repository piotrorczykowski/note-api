from datetime import datetime, timezone
from typing import Optional
from sqlmodel import TIMESTAMP, Field, SQLModel
from sqlalchemy import func


class AuditMixin(SQLModel, table=False):
    created_at: datetime = Field(
        nullable=False,
        default_factory=datetime.now(timezone.utc),
        sa_column_kwargs={
            "server_default": func.now(),
        },
        sa_type=TIMESTAMP(timezone=True),
    )

    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={
            "onupdate": func.now(),
        },
        sa_type=TIMESTAMP(timezone=True),
    )
