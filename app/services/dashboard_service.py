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
            
            return KPIMetrics(
                total_providers=total_providers,
                total_patients=total_patients,
                total_cases=total_cases
            )
    except Exception as e:
        logger.error(f"Error fetching KPI metrics: {e}")
        # Return zeros or raise if preferred, keeping it safe for now
        return KPIMetrics(total_providers=0, total_patients=0, total_cases=0)
    finally:
        if conn and conn.is_connected():
            conn.close()
