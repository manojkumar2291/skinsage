from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# --- CMS / Pages Models ---
class PageUpsert(BaseModel):
    slug: str
    title: str
    content: str
    language: Optional[str] = 'en'
    is_active: Optional[bool] = True
    updated_by: int # ID of the admin making the change

class PageResponse(BaseModel):
    title: str
    content: str
    updated_at: datetime

class PageIDResponse(BaseModel):
    page_id: int
    action: str # "created" or "updated"

# --- Testimonials Models ---
class TestimonialCreate(BaseModel):
    user_name: str
    feedback: str
    rating: int = Field(..., ge=1, le=5) # Enforce 1-5 rating

class TestimonialDTO(BaseModel):
    id: int
    user_name: str
    feedback: str
    rating: int
    created_at: datetime

class TestimonialListResponse(BaseModel):
    list: List[TestimonialDTO]

class TestimonialIDResponse(BaseModel):
    testimonial_id: int