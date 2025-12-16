from fastapi import APIRouter, HTTPException, Depends
from typing import List
import mysql.connector
from datetime import datetime
from app.database.mysql_conn import get_db_connection
from app.schemas.visits import VisitSummaryCreate, SummaryUploadResponse, VisitSummaryDTO, ChatStartResponse, ChatMessageCreate, ChatMessageResponse
import json
from app.schemas.prescription import PrescriptionCreate, PrescriptionResponse
from app.core.deps import get_current_user
router = APIRouter()


@router.post("/visits/{appointment_id}/summary", response_model=SummaryUploadResponse)
def upload_visit_summary(appointment_id: int, data: VisitSummaryCreate):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    
    try:
        sql = """
        INSERT INTO visit_summaries (appointment_id, provider_id, diagnosis, summary_text, next_steps, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        created_at = datetime.now()
        values = (
            appointment_id,
            data.provider_id,
            data.diagnosis,
            data.summary_text,
            data.next_steps,
            created_at
        )
        
        cursor.execute(sql, values)
        conn.commit()
        
        return {"summary_id": cursor.lastrowid}

    except mysql.connector.Error as err:
        conn.rollback()
        if err.errno == 1062:
            raise HTTPException(status_code=400, detail="Summary already exists for this appointment")
        raise HTTPException(status_code=500, detail=f"Database Error: {err}")
    finally:
        cursor.close()
        conn.close()


@router.get("/visits/{appointment_id}", response_model=VisitSummaryDTO)
def get_visit_summary(appointment_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True) 
    
    try:
        sql = """
        SELECT id, appointment_id, provider_id, diagnosis, summary_text, next_steps, created_at
        FROM visit_summaries
        WHERE appointment_id = %s
        """
        
        cursor.execute(sql, (appointment_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Visit summary not found")
            
        return result

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database Error: {err}")
    finally:
        cursor.close()
        conn.close()


@router.post("/visits/{appointment_id}/follow-up", response_model=ChatStartResponse)
def start_follow_up_chat(appointment_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    
    try:
       
        check_sql = "SELECT id FROM visit_chats WHERE appointment_id = %s AND status = 'active'"
        cursor.execute(check_sql, (appointment_id,))
        existing_chat = cursor.fetchone()
        
        if existing_chat:
            return {"chat_id": existing_chat[0], "status": "active"}

        
        insert_sql = """
        INSERT INTO visit_chats (appointment_id, status, created_at)
        VALUES (%s, 'active', %s)
        """
        
        created_at = datetime.now()
        cursor.execute(insert_sql, (appointment_id, created_at))
        conn.commit()
        
        return {"chat_id": cursor.lastrowid, "status": "active"}

    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {err}")
    finally:
        cursor.close()
        conn.close()

@router.post("/visits/{appointment_id}/prescription", response_model=PrescriptionResponse)
def create_prescription(
    appointment_id: int, 
    data: PrescriptionCreate,
    current_user = Depends(get_current_user)
):
    # Only Provider
    if current_user['role'] != 'provider':
        raise HTTPException(403, "Only doctors can prescribe")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Convert list of objects to JSON string for MySQL
        meds_json = json.dumps([m.dict() for m in data.medications])

        cursor.execute("""
            INSERT INTO prescriptions (appointment_id, medications, notes)
            VALUES (%s, %s, %s)
        """, (appointment_id, meds_json, data.notes))
        
        new_id = cursor.lastrowid
        conn.commit()

        return {
            "id": new_id,
            "appointment_id": appointment_id,
            "medications": data.medications,
            "notes": data.notes,
            "created_at": datetime.now()
        }
    finally:
        cursor.close()
        conn.close()
@router.get("/chats/{chat_id}/messages", response_model=List[ChatMessageResponse])
def get_chat_messages(
    chat_id: int, 
    current_user = Depends(get_current_user)
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # A. Security Check: Is the user part of this appointment?
        # We join visit_chats -> appointments to find patient_id and provider_id
        # Note: We need to find the user_id of the provider from the providers table
        cursor.execute("""
            SELECT 
                a.patient_id, 
                p.user_id as provider_user_id 
            FROM visit_chats vc
            JOIN appointments a ON vc.appointment_id = a.id
            JOIN providers p ON a.provider_id = p.id
            WHERE vc.id = %s
        """, (chat_id,))
        
        chat_info = cursor.fetchone()
        
        if not chat_info:
            raise HTTPException(404, "Chat not found")
            
        # Allow if user is Patient, Provider, or Admin
        if (current_user["id"] != chat_info['patient_id'] and 
            current_user['id'] != chat_info['provider_user_id'] and 
            current_user.role != 'admin'):
            raise HTTPException(403, "Access denied to this chat")

        # B. Fetch Messages
        cursor.execute("""
            SELECT 
                m.id, 
                m.visit_chat_id, 
                m.sender_id, 
                m.message, 
                m.created_at,
                u.role as sender_role
            FROM visit_chat_messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.visit_chat_id = %s
            ORDER BY m.created_at ASC
        """, (chat_id,))
        
        messages = cursor.fetchall()
        return messages

    except Exception as e:
        print(f"Error fetching messages: {e}")
        raise HTTPException(500, "Failed to retrieve messages")
    finally:
        cursor.close()
        conn.close()


@router.post("/chats/{chat_id}/messages", response_model=ChatMessageResponse)
def send_chat_message(
    chat_id: int, 
    data: ChatMessageCreate, 
    current_user = Depends(get_current_user)
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        user_id = current_user['id'] 
        print(f"User {user_id} sending message to chat {chat_id}")
        # 1. Security Check: Join Tables to find Patient & Provider
        # We need to know WHO the patient is and WHO the provider is for this chat
        check_sql = """
            SELECT 
                vc.status, 
                a.patient_id, 
                p.user_id as provider_user_id 
            FROM visit_chats vc
            JOIN appointments a ON vc.appointment_id = a.id
            JOIN providers p ON a.provider_id = p.id 
            WHERE vc.id = %s
        """
        cursor.execute(check_sql, (chat_id,))
        chat_info = cursor.fetchone()
        print(chat_info)

        if not chat_info:
            raise HTTPException(404, "Chat not found")

        if chat_info['status'] != 'active':
            raise HTTPException(400, "Chat is closed")

       
        is_patient = (chat_info['patient_id'] == user_id)
        is_provider = (chat_info['provider_user_id'] == user_id)
        
        if not (is_patient or is_provider):
             raise HTTPException(403, "Access denied: You are not a participant")

        # 3. Insert Message
        insert_sql = """
            INSERT INTO visit_chat_messages (visit_chat_id, sender_id, message, created_at)
            VALUES (%s, %s, %s, %s)
        """
        created_at = datetime.now()
        cursor.execute(insert_sql, (chat_id, user_id, data.message, created_at))
        conn.commit()
        
        new_id = cursor.lastrowid
        
        return {
            "visit_chat_id": chat_id,
            "id": new_id,
            "sender_id": user_id,
            "message": data.message,
            "created_at": created_at,
            "sender_name": current_user.get('full_name') 
        }

    except mysql.connector.Error as e:
        conn.rollback()
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    finally:
        cursor.close()
        conn.close()
    