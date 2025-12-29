from pydantic import BaseModel


class PagingMetadata(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
