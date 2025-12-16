from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Request model for uploading a summary
class VisitSummaryCreate(BaseModel):
    provider_id: int
    diagnosis: str
    summary_text: str
    next_steps: Optional[str] = None

# Response model for uploading (returns just ID)
class SummaryUploadResponse(BaseModel):
    summary_id: int

# Response model for Viewing the summary
class VisitSummaryDTO(BaseModel):
    id: int
    appointment_id: int
    provider_id: int
    diagnosis: str
    summary_text: str
    next_steps: Optional[str]
    created_at: datetime

# Response model for Starting a chat
class ChatStartResponse(BaseModel):
    chat_id: int
    status: str

class ChatMessageCreate(BaseModel):
    message: str

class ChatMessageResponse(BaseModel):
    id: int
    visit_chat_id: int
    sender_id: int
    sender_role: Optional[str] = None
    message: str
    created_at: datetime