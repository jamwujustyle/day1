from pydantic import BaseModel, Field
from typing import List, Optional


class ThreadMetadata(BaseModel):
    # TODO: CHANGE LATER
    name: str = Field(..., max_length=150)
    summary: str = Field(...)
    keywords: List[str]


class UpdatedThreadMetadata(BaseModel):
    summary: str
    keywords: List[str]


class OpenAIThreadResponse(BaseModel):
    match_found: bool
    matched_thread_index: Optional[int]
    update_required: bool
    updated_metadata: Optional[UpdatedThreadMetadata]
    should_create_new_thread: bool
    new_thread_metadata: Optional[ThreadMetadata]
    reasoning: str
