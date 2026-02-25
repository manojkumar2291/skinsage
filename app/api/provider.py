from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile, Query
from typing import List,Optional
from decimal import Decimal
from app.schemas.provider import ProviderCreate, ProviderResponse , ProviderUpdate, SlotGenerationRequest, SlotUpdateRequest, SlotResponse, AdminVerifyProvider
from datetime import datetime, date, time, timedelta
from app.services.provider_service import ProviderService 
from app.core.deps import role_required ,get_current_user# Import your role checker
from app.database.mysql_conn import get_db_connection as get_db
import shutil
import os

router = APIRouter(tags=["provider"])
service = ProviderService()



@router.post("/providers", response_model=ProviderResponse)
def create_provider(
    data: ProviderCreate, 
    # CRITICAL CHANGE: Only admins can access this
    current_user: dict = Depends(role_required("admin"))
):
    return service.create_provider(data)

# --- PUBLIC / AUTHENTICATED ROUTES ---

@router.get("/providers", response_model=List[ProviderResponse])
def list_providers(
    limit: int = 10,
    offset: int = 0,
    name: Optional[str] = None,
    specialty: Optional[str] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    min_experience: Optional[int] = None,
    availability: str = Query(default=None, description="Filter: 'now', 'today', 'tomorrow', 'this_week', 'this_month', or a specific date 'YYYY-MM-DD'")
):
    return service.list_providers(limit, offset, name, specialty, min_price, max_price, min_experience, availability)

@router.get("/providers/{provider_id}", response_model=ProviderResponse)
def get_provider(provider_id: int):
    return service.get_provider_by_id(provider_id)




@router.post("/slot/{provider_id}", response_model=List[SlotResponse])
def generate_slots(
    provider_id: int,
    config: SlotGenerationRequest,
    current_user: dict = Depends(role_required("admin", "provider"))
):
    db = get_db()
    cursor = db.cursor()
    new_slots = []

    # Helper to strip seconds/microseconds
    def normalize(dt: datetime):
        return dt.replace(second=0, microsecond=0)

    current_date = config.start_date

    while current_date <= config.end_date:
        # Combine Date + Time
        start_dt_obj = datetime.combine(current_date, config.start_time)
        
        # 1. Normalize (Remove seconds)
        current_dt = normalize(start_dt_obj)
        
        end_dt_limit = normalize(datetime.combine(current_date, config.end_time))

        while current_dt + timedelta(minutes=config.duration_minutes) <= end_dt_limit:
            slot_end = normalize(current_dt + timedelta(minutes=config.duration_minutes))

            # 2. Format as String for SQL (Crucial for matching)
            # This ensures MySQL sees "2025-12-10 09:00:00" exactly
            fmt_start_time = current_dt.strftime('%Y-%m-%d %H:%M:%S')
            fmt_end_time = slot_end.strftime('%Y-%m-%d %H:%M:%S')

            # Check overlap
            cursor.execute("""
                SELECT 1 FROM appointment_slots 
                WHERE provider_id = %s 
                AND start_time = %s
            """, (provider_id, fmt_start_time))

            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO appointment_slots 
                    (provider_id, start_time, end_time, is_available, is_booked)
                    VALUES (%s, %s, %s, %s, %s)
                """, (provider_id, fmt_start_time, fmt_end_time, True, False))

                new_id = cursor.lastrowid

                new_slots.append({
                    "id": new_id,
                    "provider_id": provider_id,
                    "start_time": fmt_start_time,
                    "end_time": fmt_end_time,
                    "is_available": True,
                    "is_booked": False
                })

            current_dt = slot_end

        current_date += timedelta(days=1)

    db.commit()
    cursor.close()
    return new_slots


@router.put("/slot/{provider_id}")
def update_slots(
    provider_id: int,
    update_data: SlotUpdateRequest,
    
    current_user: dict = Depends(role_required("admin","provider"))
):
    db = get_db()
    cursor = db.cursor()
    
    if not update_data.slot_ids:
        return []

 
    placeholders = ', '.join(['%s'] * len(update_data.slot_ids))
    
    
    query = f"""
        UPDATE appointment_slots 
        SET is_available = %s 
        WHERE provider_id = %s 
        AND is_booked = 0 
        AND id IN ({placeholders})
    """
    
    # Params: [is_available, provider_id, id1, id2, id3...]
    params = [update_data.is_available, provider_id] + update_data.slot_ids
    cursor.execute(query, params)
    db.commit()

    # 2. Fetch the updated rows to return them (since MySQL can't RETURNING)
    select_query = f"""
        SELECT id, provider_id, start_time, end_time, is_available, is_booked
        FROM appointment_slots
        WHERE id IN ({placeholders})
    """
    cursor.execute(select_query, update_data.slot_ids)
    updated_rows = cursor.fetchall()
    cursor.close()

    return [
        {
            "id": row[0],
            "provider_id": row[1],
            "start_time": row[2],
            "end_time": row[3],
            "is_available": bool(row[4]), # Ensure boolean for JSON
            "is_booked": bool(row[5])
        } for row in updated_rows
    ]

@router.get("/slot/{provider_id}", response_model=List[SlotResponse])
def get_provider_slots(

    provider_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    
):
    db = get_db()
    cursor = db.cursor()
    
    query = """
        SELECT id, provider_id, start_time, end_time, is_available, is_booked 
        FROM appointment_slots 
        WHERE provider_id = %s 
        AND is_available = 1 
        And is_onhold = 0
        AND is_booked = 0
        AND start_time > NOW() 
    """
    params = [provider_id]

    if start_date:
        query += " AND start_time >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND start_time < %s"
        params.append(end_date + timedelta(days=1))

    query += " ORDER BY start_time ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()

    return [
        {
            "id": row[0],
            "provider_id": row[1],
            "start_time": row[2],
            "end_time": row[3],
            "is_available": bool(row[4]),
            "is_booked": bool(row[5])
        } for row in rows
    ]


@router.post("/documents")
def upload_provider_docs(
    type: str = Form(...), # license, id_proof
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    if current_user['role']!= 'provider':
        raise HTTPException(403, "Only providers can upload documents")

    # 1. Save File
    upload_dir = "uploads/documents"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{current_user['id']}_{type}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. DB Insert
    conn =get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get Provider ID
        cursor.execute("SELECT id FROM providers WHERE user_id=%s", (current_user['id'],))
        provider = cursor.fetchone()
        
        cursor.execute("""
            INSERT INTO provider_documents (provider_id, document_type, file_url)
            VALUES (%s, %s, %s)
        """, (provider['id'], type, file_path))
        conn.commit()
        return {"msg": "Document uploaded"}
    finally:
        cursor.close()
        conn.close()

@router.patch("/{provider_id}/verify")
def verify_provider(

    provider_id: int, 
    data: AdminVerifyProvider,
    current_user = Depends(get_current_user)
):
    if current_user['role'] != 'admin':
        raise HTTPException(403, "Admin access required")

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE providers SET verification_status=%s WHERE id=%s
        """, (data.status, provider_id))
        conn.commit()
        return {"msg": f"Provider status updated to {data.status}"}
    finally:
        cursor.close()
        conn.close()
@router.get('/documets/{provider_id}')
def get_provider_documents(provider_id: int):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT document_type, file_url 
            FROM provider_documents 
            WHERE provider_id=%s
        """, (provider_id,))
        documents = cursor.fetchall()
        return documents
    finally:
        cursor.close()
        conn.close()