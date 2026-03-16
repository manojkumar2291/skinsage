from fastapi import APIRouter, Depends
from typing import List, Optional
from app.schemas.case import CaseCreate, CaseResponse, CaseStatusUpdate
from app.services.case_service import CaseService
from app.core.deps import get_current_user

router = APIRouter()

def get_case_service():
    return CaseService()

# 1. Create new case
@router.post("/cases", response_model=CaseResponse)
def create_case(
    data: CaseCreate, 
    current_user: dict = Depends(get_current_user),
    service: CaseService = Depends(get_case_service)
):
    # Pass user_id from the token
    return service.create_case(user_id=current_user['id'], data=data)

# 2. List cases for the logged-in user

@router.get("/cases", response_model=List[CaseResponse])
def list_cases(
    limit: int = 10,
    offset: int = 0,
    search_user_id: Optional[int] = None,
    ai_chat_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    service: CaseService = Depends(get_case_service)
):
    return service.list_user_cases(
        current_user=current_user,
        limit=limit,
        offset=offset,
        search_user_id=search_user_id,
        ai_chat_id=ai_chat_id
    )

# 3. Get Case Details
@router.get("/cases/{case_id}", response_model=CaseResponse)
def get_case(
    case_id: int, 
    current_user: dict = Depends(get_current_user),
    service: CaseService = Depends(get_case_service)
):
    return service.get_case_details(
        case_id=case_id, 
        user_id=current_user['id'], 
        user_role=current_user.get('role', 'user')
    )

# 4. Update Case Status
@router.patch("/cases/{case_id}/status")
def update_status(
    case_id: int, 
    data: CaseStatusUpdate, 
    current_user: dict = Depends(get_current_user),
    service: CaseService = Depends(get_case_service)
):
    return service.update_case_status(
        case_id=case_id, 
        status=data.status, 
        user_id=current_user['id'],
        user_role=current_user.get('role', 'user')
    )