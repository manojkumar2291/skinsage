from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime, date, time

class AppointmentStatus(str, Enum):
    BOOKED = "booked"
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# INPUT: Patient requests an appointment
class AppointmentCreate(BaseModel):
    case_id: Optional[int] = None
    provider_id: int
    preferred_date: date
    preferred_time: time

# INPUT: Provider confirms or updates status
class AppointmentUpdate(BaseModel):
    status: AppointmentStatus
    confirmed_slot: Optional[datetime] = None
    

# OUTPUT: API Response
class AppointmentResponse(BaseModel):
    id: int
    case_id: Optional[int]= None
    patient_id: int
    provider_id: int
    provider_name: Optional[str] = None
    provider_specialty: Optional[str] = None
    preferred_slot: datetime
    confirmed_slot: Optional[datetime]
    status: AppointmentStatus
    video_link: Optional[str]
    created_at: datetime