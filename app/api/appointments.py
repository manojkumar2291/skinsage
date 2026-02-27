from fastapi import APIRouter, Depends,BackgroundTasks
from typing import List,Optional
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from app.services.appointment_service import AppointmentService
from app.core.deps import get_current_user


router = APIRouter(tags=["Appointments"])
service = AppointmentService()


@router.post("/appointments/book")
def book_appointment(
    data: AppointmentCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Initiates the booking and creates a pending_payment appointment."""
    return service.create_pending_appointment(current_user['id'], data, background_tasks)


@router.get("/appointments", response_model=List[AppointmentResponse])
def list_appointments(current_user: dict = Depends(get_current_user)):
    print(current_user)
    return service.list_appointments(
        user_id=current_user['id'], 
        role=current_user.get('role', 'user')
    )

# 3. Get Appointment Details
@router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int, current_user: dict = Depends(get_current_user)):
    return service.get_appointment(
        appointment_id=appointment_id,
        user_id=current_user['id'],
        role=current_user.get('role', 'user')
    )

# 4. Confirm/Update Appointment (Providers/Admins)
# Note: Using PATCH as we are updating partial details
@router.patch("/appointments/{appointment_id}/confirm")
def confirm_appointment(
    appointment_id: int, 
    data: AppointmentUpdate, 
    current_user: dict = Depends(get_current_user)
):
    return service.update_status(
        appointment_id=appointment_id,
        data=data,
        user_id=current_user['id'],
        role=current_user.get('role', 'user')
    )

@router.patch("/appointments/confirm")
def confirm_payment(
    reservation_id: int,
    case_id: Optional[int] = None,
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(get_current_user)
):
    return service.confirm_payment(reservation_id, case_id, background_tasks)

@router.put("/appointments/{appointment_id}")
def cancel_appointment(
    appointment_id: int,
    current_user: dict = Depends(get_current_user)
):
    return service.cancel_appointment(
        appointment_id=appointment_id,
        user_id=current_user['id'],
        role=current_user.get('role', 'user')
    )