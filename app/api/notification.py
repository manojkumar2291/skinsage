from fastapi import APIRouter, HTTPException
from datetime import datetime
import mysql.connector

# Import your DB connection and Schemas
from app.database.mysql_conn import get_db_connection 
from app.schemas.notifications import NotificationCreate, SendResponse, ListResponse
from app.utils.email_templetes import booking_confirmation_template, appointment_reminder_template

# Import the new email service
from app.services.email_service import send_email_sync

router = APIRouter()

@router.post("/notifications/send", response_model=SendResponse)
def send_notification(data: NotificationCreate):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True) 
    
    final_status = "pending"
    
    try:
        # --- STEP 1: Get User's Email ---
        # We cannot send an email if we don't know the address.
        user_sql = "SELECT email,full_name FROM users WHERE id = %s"
        cursor.execute(user_sql, (data.user_id,))
        user_row = cursor.fetchone()

        if not user_row:
             raise HTTPException(status_code=404, detail="User not found")
        
        user_email = user_row['email']

        # --- STEP 2: Send Email (Only if type is email) ---
        if data.type.value == 'email':
            try:
                
                subject,body=booking_confirmation_template(user_row['full_name'], "hii ",12-26-82024, "10:00 AM")
                
                send_email_sync(user_email, subject, body)
                final_status = "sent"
            except Exception as email_err:
                print(f"Email sending failed: {email_err}")
                final_status = "failed"
        else:
            # Handle SMS/Push logic here later
            final_status = "pending" 

        # --- STEP 3: Save Log to Database ---
        sql = """
        INSERT INTO notifications (user_id, type, subject, body, status, sent_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        sent_time = datetime.now()
        
        values = (
            data.user_id,
            data.type.value,
            data.subject,
            data.body,
            final_status,
            sent_time
        )
        
        cursor.execute(sql, values)
        conn.commit()
        
        return {"status": final_status}

    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {err}")
    except HTTPException as he:
        raise he
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# The GET endpoint remains the same as your previous code
@router.get("/notifications", response_model=ListResponse)
def get_notifications(user_id: int = 1):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        sql = """
        SELECT id, user_id, type, subject, body, status, sent_at
        FROM notifications
        WHERE user_id = %s
        ORDER BY id DESC
        """
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        return {"notifications": rows}

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database Error: {err}")
    finally:
        cursor.close()
        conn.close()