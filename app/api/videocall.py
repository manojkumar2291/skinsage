from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from agora_token_builder import RtcTokenBuilder
from app.schemas.videocall import TokenRequest
import time
from datetime import datetime, timedelta

# Import your database dependency (adjust this import to match your project)
from app.database.mysql_conn import get_db_connection as get_db

load_dotenv()

router = APIRouter()

APP_ID = os.getenv("AGORA_APP_ID")
APP_CERTIFICATE = os.getenv("AGORA_APP_CERTIFICATE")

@router.post("/get-agora-token")
def generate_token(request: TokenRequest, db = Depends(get_db)):
    cursor = db.cursor() # 1. Create Cursor
    
    try:
        appt_id = int(request.channel_name)
    except ValueError:
        raise HTTPException(status_code=400, detail="Channel name must be a valid Appointment ID")

    # 2. Fix Query Syntax (Use %s for MySQL)
    query = "SELECT preferred_slot FROM appointments WHERE id = %s LIMIT 1"
    
    # 3. Execute using cursor and tuple
    cursor.execute(query, (appt_id,))
    result = cursor.fetchone()

    # Close cursor immediately after fetching to free resources
    cursor.close()

    if not result:
        raise HTTPException(status_code=404, detail="Appointment not found")

    scheduled_time = result[0] # Access by index since it's a tuple

    # Calculate allowed time (10 minutes buffer)
    buffer_window = timedelta(minutes=10)
    allowed_start_time = scheduled_time - buffer_window
    current_time_utc = datetime.utcnow()

    # The Check: Is it too early?
    # Note: Ensure DB time and System time match (UTC vs Local). 
    # If DB stores IST, convert current_time_utc to IST before comparing.
    if current_time_utc < allowed_start_time:
        minutes_left = int((allowed_start_time - current_time_utc).total_seconds() / 60)
        minutes_left = max(1, minutes_left)
        
        raise HTTPException(
            status_code=403, 
            detail=f"Too early. You can join in {minutes_left} minutes."
        )

    # Token Generation Logic
    expiration_time = 3600  # 1 hour
    current_timestamp = int(time.time())
    privilege_expire = current_timestamp + expiration_time

    if request.role == "publisher":
        role = 1
    else:
        role = 2

    token = RtcTokenBuilder.buildTokenWithUid(
        APP_ID,
        APP_CERTIFICATE,
        request.channel_name,
        request.uid,
        role,
        privilege_expire
    )

    return {
        "token": token,
        "appId": APP_ID,
        "channelName": request.channel_name,
        "uid": request.uid
    }
    