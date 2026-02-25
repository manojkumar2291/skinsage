from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class RegisterSchema(BaseModel):
    name: str
    email: str
    password: str

class LoginSchema(BaseModel):
    email: str
    password: str

class GoogleLoginSchema(BaseModel):
    token: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    language_pref: Optional[str] = None
    profile_photo: Optional[str] = None

class UserResponse(UserUpdate):
    id: int
    email: str
    class Config:
        from_attributes = True