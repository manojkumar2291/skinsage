from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

# Enums to match MySQL
class NotificationType(str, Enum):
    email = "email"
    sms = "sms"
    push = "push"

class NotificationStatus(str, Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"


class NotificationCreate(BaseModel):
    user_id: int
    type: NotificationType
    subject: str
    body: str

class NotificationDTO(BaseModel):
    id: int
    user_id: int
    type: str
    subject: str
    body: str
    status: str
    sent_at: Optional[datetime]


class SendResponse(BaseModel):
    status: str

class ListResponse(BaseModel):
    notifications: List[NotificationDTO]