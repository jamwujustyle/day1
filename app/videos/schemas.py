from pydantic import Field, BaseModel, HttpUrl
from datetime import datetime
from typing import Optional
from uuid import UUID


class VideoBase(BaseModel):
    title: str = Field(..., description="Title of the video")
    description: Optional[str] = Field(
        None, description="Optional description of the video (can be updated)"
    )


class VideoCreate(VideoBase):
    file_url: HttpUrl = Field(..., description="URL of the uploaded video")


class VideoResponse(VideoBase):
    id: UUID = Field(..., description="Uniqie identifier of the video")
    user_id: UUID = Field(..., description="Author of the video")
    file_url: HttpUrl = Field(..., description="Cloud storage URL for the video")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True
