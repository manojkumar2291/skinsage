from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatMessageCreate(BaseModel):
    message: str

class ChatMessageResponse(BaseModel):
    id: int
    sender_id: int
    message: str
    created_at: datetime
    sender_role: Optional[str] = None