from app.database.mysql_conn import get_db_connection
from app.schemas.dashboard import KPIMetrics
import logging

logger = logging.getLogger(__name__)

def get_kpi_metrics() -> KPIMetrics:
    """
    Fetches KPI metrics from the database.
    - Total Providers: Count from 'providers' table.
    - Total Patients: Count from 'users' table where role is 'patient'.
    - Total Cases: Count from 'cases' table.
    - Closed Cases: Count from 'cases' table where status is 'closed'.
    - Total Appointments: Count from 'appointments' table.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Get Total Providers
            cur.execute("SELECT COUNT(*) FROM providers")
            total_providers = cur.fetchone()[0]
            
            # Get Total Patients
            cur.execute("SELECT COUNT(*) FROM users WHERE role = 'patient'")
            total_patients = cur.fetchone()[0]
            
            # Get Total Cases
            cur.execute("SELECT COUNT(*) FROM cases")
            total_cases = cur.fetchone()[0]

            # Get Closed Cases
            cur.execute("SELECT COUNT(*) FROM cases WHERE status = 'closed'")
            closed_cases = cur.fetchone()[0]

            # Get Total Appointments
            cur.execute("SELECT COUNT(*) FROM appointments")
            total_appointments = cur.fetchone()[0]
            
            return KPIMetrics(
                total_providers=total_providers,
                total_patients=total_patients,
                total_cases=total_cases,
                closed_cases=closed_cases,
                total_appointments=total_appointments
            )
    except Exception as e:
        logger.error(f"Error fetching KPI metrics: {e}")
        return KPIMetrics(
            total_providers=0, 
            total_patients=0, 
            total_cases=0,
            closed_cases=0,
            total_appointments=0
        )
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_patients_list():
    """
    Fetches a list of all patients from the users table.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT id, full_name, email, phone, dob, gender, language_pref, created_at FROM users WHERE role = 'patient' ORDER BY created_at DESC")
            patients = cur.fetchall()
            return patients
    except Exception as e:
        logger.error(f"Error fetching patients list: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()
