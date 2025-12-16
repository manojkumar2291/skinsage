from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MedicationItem(BaseModel):
    name: str
    dosage: str # e.g., "500mg"
    frequency: str # e.g., "1-0-1"
    duration: str # e.g., "5 days"

class PrescriptionCreate(BaseModel):
    medications: List[MedicationItem]
    notes: Optional[str] = None

class PrescriptionResponse(PrescriptionCreate):
    id: int
    appointment_id: int
    created_at: datetime