from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.paging import PagingMetadata


class NoteQuery(BaseModel):
    q: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


class NoteUpsert(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    content: str = Field(
        ...,
        min_length=1,
        max_length=1000,
    )


class NoteResponse(BaseModel):
    id: int
    title: Optional[str]
    content: str
    model_config = {"from_attributes": True}


class NoteList(BaseModel):
    data: List[NoteResponse]
    meta: PagingMetadata
