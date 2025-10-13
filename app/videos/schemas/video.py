from pydantic import Field, BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from .subtitle import SubtitleResponse


class VideoLocalizationResponse(BaseModel):
    language: str
    title: str
    summary: str

    class Config:
        from_attributes = True


class VideoResponse(BaseModel):
    id: UUID = Field(..., description="Uniqie identifier of the video")
    user_id: UUID = Field(..., description="Author of the video")
    file_url: str = Field(..., description="Relative path to the video file")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    title: Optional[str] = None
    description: Optional[str] = None
    subtitles: List[SubtitleResponse] = []
    localizations: List[VideoLocalizationResponse] = []

    model_config = ConfigDict(from_attributes=True)
