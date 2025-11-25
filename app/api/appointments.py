from fastapi import APIRouter, Depends
from typing import List
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from app.services.appointment_service import AppointmentService
from app.core.deps import get_current_user, role_required

router = APIRouter(tags=["Appointments"])
service = AppointmentService()

# 1. Request an Appointment (Patients)
@router.post("/appointments/request", response_model=AppointmentResponse)
def request_appointment(
    data: AppointmentCreate, 
    current_user: dict = Depends(get_current_user)
):
    return service.request_appointment(patient_id=current_user['id'], data=data)

# 2. List Appointments (Smart filter: Patients see theirs, Doctors see theirs)
@router.get("/appointments", response_model=List[AppointmentResponse])
def list_appointments(current_user: dict = Depends(get_current_user)):
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