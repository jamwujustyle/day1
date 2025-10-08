from pydantic import Field, BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


from typing import Optional


class UserResponse(BaseModel):
    id: UUID = Field(..., description="Unique identifier of the User")
    email: str = Field(..., description="User's email address")
    username: str = Field(..., description="User's username")
    avatar: Optional[str] = Field(None, description="URL to the user's avatar image")

    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = ConfigDict(from_attributes=True)
