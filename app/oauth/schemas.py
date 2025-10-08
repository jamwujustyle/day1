from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime


class UserResponse(BaseModel):
    id: UUID = Field(..., description="Unique identifier of the User")
    email: str = Field(..., description="User's email address")
    username: str = Field(..., description="User's username")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class OAuthCallbackResponse(BaseModel):
    user: UserResponse = Field(..., description="User information")
    is_new_user: bool = Field(..., description="Whether this is a newly created user")

    model_config = ConfigDict(from_attributes=True)
