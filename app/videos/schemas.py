from pydantic import Field, BaseModel, HttpUrl, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID


class VideoBase(BaseModel):
    title: str = Field(..., description="Title of the video")
    description: Optional[str] = Field(
        None, description="Optional description of the video (can be updated)"
    )


class VideoCreate(VideoBase):
    pass


class VideoResponse(VideoBase):
    id: UUID = Field(..., description="Uniqie identifier of the video")
    user_id: UUID = Field(..., description="Author of the video")
    file_url: str = Field(..., description="Relative path to the video file")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
