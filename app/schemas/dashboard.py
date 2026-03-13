from pydantic import BaseModel

class KPIMetrics(BaseModel):
    total_providers: int
    total_patients: int
    total_cases: int
