from fastapi import APIRouter, Depends
from typing import List
from app.schemas.provider import ProviderCreate, ProviderResponse
from app.services.provider_service import ProviderService
from app.core.deps import role_required # Import your role checker

router = APIRouter(tags=["provider"])
service = ProviderService()

# --- ADMIN ONLY ROUTES ---

@router.post("/providers", response_model=ProviderResponse)
def create_provider(
    data: ProviderCreate, 
    # CRITICAL CHANGE: Only admins can access this
    current_user: dict = Depends(role_required("admin"))
):
    return service.create_provider(data)

# --- PUBLIC / AUTHENTICATED ROUTES ---

@router.get("/providers", response_model=List[ProviderResponse])
def list_providers():
    return service.list_providers()

@router.get("/providers/{provider_id}", response_model=ProviderResponse)
def get_provider(provider_id: int):
    # Pass logic to service (assumed existing from previous step)
    # You need to ensure get_provider_by_id exists in your service
    return service.get_provider_by_id(provider_id)
