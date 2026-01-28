from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date
from enum import Enum

# --- ENUMS ---
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class Role(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"

class ConsentTypeEnum(str, Enum):
    PRIVACY = "privacy"
    TERMS = "terms"
    PARENTAL = "parental"

class ConsentStatusEnum(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"



class RegisterSchema(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    role: Role = Role.PATIENT
    dob: Optional[date] = None
    gender: Optional[Gender] = None
    language_pref: str = "en"

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class GoogleLoginSchema(BaseModel):
    token: str

class MicrosoftLoginSchema(BaseModel):
    token: str

class RefreshSchema(BaseModel):
    refresh_token: str

class CompleteProfileSchema(BaseModel):
  
    phone: str

    dob: str        
    gender: str     
    language_pref: Optional[str] = "en"

class ConsentUpdateSchema(BaseModel):
    consent_type: ConsentTypeEnum
    status: ConsentStatusEnum



class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: Optional[str]
    profile_complete: Optional[bool] = None

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
    profile_complete: Optional[bool] = True



class OTPGenerateRequest(BaseModel):
    identifier: str # Email or Phone

class OTPVerifyRequest(BaseModel):
    identifier: str
    code: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str