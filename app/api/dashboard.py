from fastapi import APIRouter, Depends
from app.services.dashboard_service import get_kpi_metrics, get_patients_list
from app.schemas.dashboard import KPIMetrics
from app.core.deps import get_current_user, role_required
from typing import List

router = APIRouter()

@router.get("/kpi", response_model=KPIMetrics)
def fetch_kpi_metrics(current_user=Depends(role_required('admin'))):
    """
    Fetch KPI metrics for the admin dashboard.
    Required role: admin
    """
    return get_kpi_metrics()

@router.get("/patients")
def fetch_patients_list(current_user=Depends(role_required('admin'))):
    """
    Fetch a list of all patients for the admin dashboard.
    Required role: admin
    """
    return get_patients_list()
