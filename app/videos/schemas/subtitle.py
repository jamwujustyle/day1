from pydantic import Field, BaseModel
from uuid import UUID


class SubtitleResponse(BaseModel):
    id: UUID
    language: str

    class Config:
        from_attributes = True
