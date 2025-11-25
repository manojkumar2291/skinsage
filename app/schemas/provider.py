from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from enum import Enum

class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

# INPUT: Admin sends this data
class ProviderCreate(BaseModel):
    user_id: int 
    name:str
    license_number: str
    specialty: str
    experience_years: int
    languages: List[str]
    consultation_fee: Decimal
    bio: Optional[str] = None
    profile_photo: Optional[str] = None

# INPUT: Admin updates status
class ProviderStatusUpdate(BaseModel):
    verification_status: VerificationStatus

# OUTPUT: Response structure
class ProviderResponse(BaseModel):
    id: int
    user_id: int
    name:str
    license_number: str
    specialty: str
    verification_status: VerificationStatus
    experience_years: int
    languages: List[str] | str
    consultation_fee: Decimal
    bio: Optional[str]
    profile_photo: Optional[str]