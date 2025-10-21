from pydantic import Field, BaseModel, ConfigDict, EmailStr
from datetime import datetime
from uuid import UUID


from typing import Optional


class UserResponse(BaseModel):
    id: UUID = Field(..., description="Unique identifier of the User")
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="User's username")
    avatar: Optional[str] = Field(None, description="URL to the user's avatar image")
    bio: Optional[str] = Field(None, description="AI Generated user bio")
    last_login: datetime = Field(..., description="Last login timestamp")

    model_config = ConfigDict(from_attributes=True)
