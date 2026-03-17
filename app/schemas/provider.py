from pydantic import BaseModel,EmailStr
from typing import List, Optional
from decimal import Decimal
from enum import Enum
from datetime import datetime, date, time

class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class ProviderCreate(BaseModel):
    
    name:str
    email:EmailStr
    phone: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    language_pref: Optional[str] = None
    license_number: str
    specialty: List[str]
    experience_years: int
    languages: List[str]
    consultation_fee: Decimal
    bio: Optional[str] = None
    profile_photo: Optional[str] = None


class ProviderStatusUpdate(BaseModel):
    verification_status: VerificationStatus


class AdminVerifyProvider(BaseModel):
    status: str 


class ProviderResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    license_number: str
    specialty: List[str] | str
    verification_status: VerificationStatus
    experience_years: int
    languages: List[str] | str
    consultation_fee: Decimal
    bio: Optional[str]
    profile_photo: Optional[str]

class ProviderUpdate(BaseModel):
    name: Optional[str] = None
    specialty: Optional[List[str]] = None
    consultation_fee: Optional[float] = None
    bio: Optional[str] = None
    profile_photo: Optional[str] = None
    experience_years: Optional[int] = None
    languages: Optional[List[str]] = None



class SlotGenerationRequest(BaseModel):
    start_date: date
    end_date: date
    start_time: time
    end_time: time
    duration_minutes: int = 30
    excluded_intervals: Optional[List[List[time]]] = None  # List of [start, end] time pairs

class SlotUpdateRequest(BaseModel):
    slot_ids: List[int]
    is_available: bool

class SlotResponse(BaseModel):
    id: int
    provider_id: int
    start_time: datetime
    end_time: datetime
    is_booked: bool
    is_available: bool
    class Config:
        from_attributes = True