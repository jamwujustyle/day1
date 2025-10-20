from pydantic import BaseModel, Field


class UserBioAIResponse(BaseModel):
    bio: str = Field(...)
