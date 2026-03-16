import json
import re
import uuid
from typing import List, Tuple
from pathlib import Path
from datetime import datetime

# Added Request and Response for cookie handling
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends, Request, Response 
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.concurrency import run_in_threadpool
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Tuple, Optional
from app.core.deps import get_current_user
import requests
from app.schemas.analysis import AIChatResponse

from app.core.config import settings
from app.database.mysql_conn import get_db_connection as get_connection
from app.services import image_proc, llm_proc
from collections import namedtuple

# Define the helper class here
Credentials = namedtuple('Credentials', ['credentials'])

router = APIRouter()
security = HTTPBearer(auto_error=False)

def parse_summary_to_array(text):
    data_array = []
    text = text.replace(", Condition:", "\nCondition:")
    lines = text.split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            data_array.append({
                "label": key.strip().title(), 
                "value": value.strip()
            })
    return data_array

def extract_category_and_path(messages_list: list) -> Tuple[str, str]:
    """
    Parses chat history.
    Returns a tuple: (subfolder_path, raw_category_type)
    Example: ('skin_issue/warts', 'Skin') or ('hair_issue/dandruff', 'Hair')
    """
    category = "uncategorized"
    condition = "general"
    raw_cat_type = "general" 

    pattern = r"Category:\s*(.*?),\s*Condition:\s*(.*)"

    for msg in messages_list:
        # Sometimes msg might be a string representation of a dict
        if isinstance(msg, str):
            try:
                msg = json.loads(msg)
            except:
                continue
                
        content = msg.get("content", "")
        if "Category:" in content and "Condition:" in content:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                raw_cat = match.group(1).strip()
                raw_cond = match.group(2).strip()
                
                raw_cat_type = raw_cat

                category = image_proc.sanitize_filename(raw_cat)
                condition = image_proc.sanitize_filename(raw_cond)
                break 
    
    return f"{category}/{condition}", raw_cat_type


@router.post("/chat")
async def analyze_endpoint(
    request: Request,
    response: Response,
    messages: str = Form(...),
    image_files: List[UploadFile] = File(...),
    token_creds: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    user_id = None
    guest_id = None
    
    
    # --- 1. AUTHENTICATION & GUEST LOGIC ---
    try:
        token = None
        # Priority 1: Swagger/Header via token_creds
        if token_creds:
            token = token_creds.credentials
        
        # Priority 2: Manual extraction (fallback)
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and "Bearer " in auth_header:
                token = auth_header.replace("Bearer ", "")

        if token:
            
            curr_user = await run_in_threadpool(get_current_user, Credentials(credentials=token)) 
            if curr_user:
                user_id = curr_user.get('id')
    except Exception as e:
        print(f"Auth derivation failed: {e}")

    if not user_id:
        guest_id = request.cookies.get("guest_id") 
        if not guest_id:
            guest_id = str(uuid.uuid4()) 
            # Set cookie for 30 days
            response.set_cookie(
                key="guest_id", 
                value=guest_id, 
                httponly=True, 
                max_age=2592000,
                samesite="lax"
            )

    # --- 2. INPUT VALIDATION & PARSING ---
    try:
        messages_json = json.loads(messages)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in 'messages' field")

    if not (1 <= len(image_files) <= 3):
        raise HTTPException(status_code=400, detail="Please upload 1 to 3 images.")

    subfolder_path, category_type = extract_category_and_path(messages_json)
    
    # --- 3. IMAGE NORMALIZATION & AI VALIDATION ---
    valid_images_payload = [] 
    for i, file in enumerate(image_files):
        image_bytes = await file.read()
        if not image_bytes: continue
            
        processed_image = image_proc.normalize_image_bytes(image_bytes)
        
        # Verify the image is actually a medical/skin photo
        is_valid, validation_msg = llm_proc.validate_image_is_dermatological(
            processed_image, expected_category=category_type
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Image {file.filename} rejected: {validation_msg}")
        
        valid_images_payload.append({
            "bytes": image_bytes,
            "filename": file.filename or f"upload_{i}.jpg",
            "processed": processed_image
        })

    # --- 4. IMAGE STORAGE & LLM CONTENT PREP ---
    vision_model_content = []
    image_metadata = []

    for item in valid_images_payload:
        unique_filename, server_url_path = await image_proc.save_image_to_disk(
            item["bytes"], item["filename"], subfolder=subfolder_path
        )
        image_metadata.append({"url": server_url_path})
        
        image_data_uri = image_proc.encode_image_to_base64_datauri(item["processed"])
        vision_model_content.append({"type": "image_url", "image_url": {"url": image_data_uri}})

    # --- 5. AI ANALYSIS CALL ---
    user_history = "\n".join([
        f"- {m.get('role','').upper()}: {m.get('content','')}" 
        for m in messages_json if m.get('role') == 'user'
    ])
    
    vision_model_content.insert(0, {"type": "text", "text": f"User History:\n{user_history}\n\nAnalyze these images."})

    analysis_messages = [
        {"role": "system", "content": settings.ANALYSIS_SYSTEM_PROMPT},
        {"role": "user", "content": vision_model_content}
    ]

    llm_resp = await run_in_threadpool(llm_proc.call_openrouter_model, analysis_messages)
    raw_analysis = llm_resp.json().get('choices', [{}])[0].get('message', {}).get('content', "")

    # Parse recommendation flag
    recommendation_needed = "Recommendation_Required: Yes" in raw_analysis
    clean_analysis = re.sub(r"Recommendation_Required:\s*(Yes|No)", "", raw_analysis, flags=re.I).strip()

    # --- 6. DATABASE PERSISTENCE (Safe Threading) ---
    def db_operations():
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        try:
            photo_urls = ",".join([m['url'] for m in image_metadata])
            
            # 6a. Insert AI Chat Record
            cur.execute(
                """INSERT INTO ai_chats (user_id, guest_id, input_text, ai_response, summary, red_flag, photo_url, created_at) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())""",
                (user_id, guest_id, user_history[:1000], clean_analysis, "AI Skin Analysis", int(recommendation_needed), photo_urls)
            )
            chat_id = cur.lastrowid
            case_id = None

            # 6b. Auto-create Case (ONLY for logged-in users)
            if user_id:
                case_title = f"AI Analysis - {datetime.now().strftime('%Y-%m-%d')}"
                cur.execute(
                    """INSERT INTO cases (user_id, ai_chat_id, title, symptoms, status, created_at) 
                       VALUES (%s, %s, %s, %s, 'open', NOW())""",
                    (user_id, chat_id, case_title, user_history[:2000])
                )
                case_id = cur.lastrowid
            
            conn.commit()
            return chat_id, case_id
        except Exception as e:
            conn.rollback()
            print(f"Database insertion failed: {e}")
            return None, None
        finally:
            cur.close()
            conn.close()

    new_chat_id, new_case_id = await run_in_threadpool(db_operations)

    # --- 7. FINAL RESPONSE ---
    return JSONResponse({
        "reply": clean_analysis, 
        "recommendation_needed": recommendation_needed,
        "chat_id": new_chat_id,
        "case_id": new_case_id, # Will be None for guests
        "guest_mode": (user_id is None)
    })
@router.get("/{chat_id}", response_model=AIChatResponse)
def retrieve_ai_chat(
    chat_id: int, 
    current_user = Depends(get_current_user)
):
    db = get_connection()
    cursor = db.cursor()
    
    
    cursor.execute("""
        SELECT id, user_id, input_text, ai_response, summary, created_at, photo_url, red_flag
        FROM ai_chats WHERE id = %s
    """, (chat_id,))
    
    chat = cursor.fetchone()
    cursor.close()
    db.close()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages_constructed = [
        {"role": "user", "content":parse_summary_to_array(chat[2]) },       
        {"role": "assistant", "content": chat[3]}   
    ]

    return {
        "id": chat[0],
        "user_id": chat[1],
        "summary": chat[4],     
        "messages": messages_constructed,
        "created_at": chat[5],  
        "photo_url": [chat[6]],   
        "red_flag": bool(chat[7]) 
    }

# @router.get("/health")
# def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy",
#         "model": settings.MODEL_NAME,
#         "api_configured": bool(settings.OPENROUTER_API_KEY),
#         "validation_enabled": bool(settings.HUGGINGFACE_API_KEY)
#     }