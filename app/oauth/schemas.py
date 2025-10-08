from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from ..users.schemas import UserResponse


class OAuthCallbackResponse(BaseModel):
    user: UserResponse = Field(..., description="User information")
    is_new_user: bool = Field(..., description="Whether this is a newly created user")

    model_config = ConfigDict(from_attributes=True)
