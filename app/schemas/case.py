from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

# Match your DB ENUM exactly
class CaseStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"

# INPUT: Data sent to create a case
class CaseCreate(BaseModel):
    title: str
    symptoms: str
    ai_chat_id: Optional[int] = None  # Optional: Link to an existing chat
    # photos: List[str] = []            # Optional: List of image URLs

# INPUT: For updating status
class CaseStatusUpdate(BaseModel):
    status: CaseStatus

# OUTPUT: Full details returned to frontend
class CaseResponse(BaseModel):
    id: int
    user_id: int
    ai_chat_id: Optional[int]
    title: str
    symptoms: str
    # photos: List[str] | str  # Handles both list or raw string from DB
    status: CaseStatus
    created_at: datetime