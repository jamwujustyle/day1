from pydantic import Field, BaseModel, ConfigDict, EmailStr
from datetime import datetime
from uuid import UUID


from typing import Optional, List


class UserResponse(BaseModel):
    id: UUID = Field(..., description="Unique identifier of the User")
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="User's username")
    avatar: Optional[str] = Field(None, description="URL to the user's avatar image")
    bio: Optional[str] = Field(None, description="AI Generated user bio")
    # last_login: datetime = Field(..., description="Last login timestamp")

    model_config = ConfigDict(from_attributes=True)


class UpdateUsernameRequest(BaseModel):
    new_username: str = Field(...)


class UserLogsSimpleResponse(BaseModel):
    log_id: int
    title: str = Field(...)
    summary: str = Field(...)
    thread_name: Optional[str] = None


class UserLogsListResponse(BaseModel):
    logs: List[UserLogsSimpleResponse]


class SubtitleInfo(BaseModel):
    id: UUID
    language: str


class LocalizationDetail(BaseModel):
    language: str
    title: Optional[str]
    summary: Optional[str]


class ExtendedLogResponse(BaseModel):
    log_id: int
    video_id: UUID
    file_url: str
    thread_name: Optional[str]

    localization: Optional[LocalizationDetail]
    available_subtitles: List[SubtitleInfo] = Field(default_factory=List)
    current_subtitle_id: Optional[UUID] = None
