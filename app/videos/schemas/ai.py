from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class AISegment(BaseModel):
    word: str
    start: float
    end: float


class AITranslation(BaseModel):
    title: str = Field(..., max_length=70)
    summary: str
    text: Optional[str] = None
    segments: Optional[List[AISegment]] = None
    compressed_context: Optional[str] = None


class AIMultiLanguageTranslation(BaseModel):
    translations: Dict[str, AITranslation]
