from pydantic import BaseModel
from typing import List
from datetime import datetime


class AIChatResponse(BaseModel):
    id: int
    user_id: int
    summary: str
    messages: List[dict]  # Assuming JSON storage of chat history
    created_at: datetime
    photo_url: List[str]
    red_flag: bool
    class Config:
        from_attributes = True