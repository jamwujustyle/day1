from pydantic import Field, BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


class UserResponse(BaseModel):
    id: UUID = Field(..., description="Unique identifier of the User")
    email: str = Field(..., description="User's email address")
    username: str = Field(..., description="User's username")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = ConfigDict(from_attributes=True)
